from __future__ import annotations

import dataclasses
import logging
from typing import List, Optional, Tuple

import typing_extensions

from greenbtc.types.blockchain_format.sized_bytes import bytes32, bytes48
from greenbtc.types.stake_record import StakeRecord, StakeRecordThin
from greenbtc.types.stake_value import STAKE_FARM_COUNT
from greenbtc.util.db_wrapper import SQLITE_MAX_VARIABLE_NUMBER, DBWrapper2
from greenbtc.util.ints import uint32, uint64
from greenbtc.util.lru_cache import LRUCache
from greenbtc.util.misc import to_batches

log = logging.getLogger(__name__)


@typing_extensions.final
@dataclasses.dataclass
class StakeRecordStore:
    """
    This object handles CoinRecords in DB.
    """

    db_wrapper: DBWrapper2
    stake_farm_cache: LRUCache[bytes48, List[StakeRecordThin]]
    stake_lock_cache: LRUCache[bytes32, List[StakeRecordThin]]

    @classmethod
    async def create(cls, db_wrapper: DBWrapper2) -> StakeRecordStore:
        self = StakeRecordStore(db_wrapper, LRUCache(104), LRUCache(104))
        async with self.db_wrapper.writer_maybe_transaction() as conn:
            log.info("DB: Creating coin store tables and indexes.")
            await conn.execute(
                "CREATE TABLE IF NOT EXISTS stake_record("
                "coin_name blob PRIMARY KEY,"
                " confirmed_index bigint,"
                " spent_index bigint,"  # if this is zero, it means the coin has not been spent
                " stake_puzzle_hash blob,"
                " puzzle_hash blob,"
                " stake_type tinyint,"
                " is_stake_farm tinyint,"
                " amount int,"
                " coefficient float,"
                " expiration bigint)"
            )

            # Useful for reorg lookups
            log.info("DB: Creating index stake confirmed_index")
            await conn.execute("CREATE INDEX IF NOT EXISTS stake_confirmed_index on stake_record(confirmed_index)")

            log.info("DB: Creating index stake spent_index")
            await conn.execute("CREATE INDEX IF NOT EXISTS stake_spent_index on stake_record(spent_index)")

            log.info("DB: Creating index stake stake_type")
            await conn.execute("CREATE INDEX IF NOT EXISTS stake_stake_type on stake_record(stake_type)")

            log.info("DB: Creating index stake is_stake_farm")
            await conn.execute("CREATE INDEX IF NOT EXISTS stake_is_stake_farm on stake_record(is_stake_farm)")

            log.info("DB: Creating index stake expiration")
            await conn.execute("CREATE INDEX IF NOT EXISTS stake_expiration on stake_record(expiration)")

            log.info("DB: Creating index stake stake_puzzle_hash")
            await conn.execute("CREATE INDEX IF NOT EXISTS stake_puzzle_hash on stake_record(stake_puzzle_hash)")

            log.info("DB: Creating index stake puzzle_hash")
            await conn.execute("CREATE INDEX IF NOT EXISTS puzzle_hash on stake_record(puzzle_hash)")

        return self

    # Store StakeRecord in DB
    async def _add_records(self, records: List[StakeRecord]) -> None:
        values2 = []
        for record in records:
            values2.append(
                (
                    record.name,
                    record.confirmed_block_index,
                    record.spent_block_index,
                    record.stake_puzzle_hash,
                    record.puzzle_hash,
                    record.stake_type,
                    record.is_stake_farm,
                    int(record.amount),
                    float(record.coefficient),
                    record.expiration,
                )
            )
        if len(values2) > 0:
            async with self.db_wrapper.writer_maybe_transaction() as conn:
                await conn.executemany(
                    "INSERT INTO stake_record VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    values2,
                )

    # Update stake_record to be spent in DB
    async def _set_spent(self, coin_names: List[bytes32], index: uint32) -> None:
        assert len(coin_names) == 0 or index > 0

        if len(coin_names) == 0:
            return None

        async with self.db_wrapper.writer_maybe_transaction() as conn:
            for batch in to_batches(coin_names, SQLITE_MAX_VARIABLE_NUMBER):
                name_params = ",".join(["?"] * len(batch.entries))
                await conn.execute(
                    f"UPDATE stake_record INDEXED BY sqlite_autoindex_stake_record_1 "
                    f"SET spent_index={index} "
                    f"WHERE spent_index=0 "
                    f"AND coin_name IN ({name_params})",
                    batch.entries,
                )

    async def new_stake(
            self,
            height: uint32,
            tx_additions: List[StakeRecord],
            tx_removals: List[bytes32],
    ) -> None:
        if len(tx_additions) > 0:
            await self._add_records(tx_additions)
        await self._set_spent(tx_removals, height)

    async def rollback_to_block(self, block_index: int):
        """
        Note that block_index can be negative, in which case everything is rolled back
        Returns the list of coin records that have been modified
        """
        # Add coins that are confirmed in the reverted blocks to the list of updated coins.
        async with self.db_wrapper.writer_maybe_transaction() as conn:
            # Delete reverted blocks from storage
            await conn.execute("DELETE FROM stake_record WHERE confirmed_index>?", (block_index,))
            await conn.execute("UPDATE stake_record SET spent_index=0 WHERE spent_index>?", (block_index,))

        self.stake_farm_cache = LRUCache(self.stake_farm_cache.capacity)
        self.stake_lock_cache = LRUCache(self.stake_lock_cache.capacity)

    async def get_stake_farm_count(self, stake_puzzle_hash: bytes32, timestamp: uint64) -> int:
        async with self.db_wrapper.reader_no_transaction() as conn:
            async with conn.execute(
                "SELECT SUM(1) FROM stake_record INDEXED BY stake_puzzle_hash"
                " WHERE is_stake_farm=1 AND stake_puzzle_hash=? AND expiration>? GROUP BY puzzle_hash",
                (stake_puzzle_hash, timestamp),
            ) as cursor:
                row = await cursor.fetchone()

            if row is not None:
                [count] = row
                return int(count)
            return 0
    #
    # async def get_stake_amount_sum(self, timestamp: uint64, is_stake_farm: bool) -> Tuple[int, float, int]:
    #     async with self.db_wrapper.reader_no_transaction() as conn:
    #         rows = list(
    #             await conn.execute_fetchall(
    #                 "SELECT SUM(amount),SUM(amount*coefficient) FROM stake_record WHERE "
    #                 "is_stake_farm=? and expiration>?", (1 if is_stake_farm else 0, timestamp),
    #             )
    #         )
    #     if len(rows) == 0 or rows[0][0] is None:
    #         return 0, 0
    #     return int(rows[0][0]), float(rows[0][1])

    async def get_stake_amount_total(self, timestamp: uint64) -> Tuple[int, float, int]:
        async with self.db_wrapper.reader_no_transaction() as conn:
            async with conn.execute(
                "SELECT is_stake_farm,SUM(amount),SUM(amount*coefficient) FROM stake_record "
                "WHERE expiration>? GROUP BY is_stake_farm", (timestamp,),
            ) as cursor:
                stake_farm, stake_farm_calc, stake_lock = 0, 0.0, 0
                for row in await cursor.fetchall():
                    if int(row[0]) == 0:
                        stake_lock = int(row[1])
                    else:
                        stake_farm = int(row[1])
                        stake_farm_calc = float(row[2])
        return stake_farm, stake_farm_calc, stake_lock

    async def get_stake_farm_records_thin(
        self, stake_puzzle_hash: bytes32, height: uint32, timestamp: uint64
    ) -> List[StakeRecordThin]:
        stake_key = bytes48(stake_puzzle_hash + height.to_bytes(16, "big"))
        stake_list: Optional[List[StakeRecordThin]] = self.stake_farm_cache.get(stake_key)
        if stake_list is not None:
            return stake_list
        async with self.db_wrapper.reader_no_transaction() as conn:
            async with conn.execute(
                "SELECT stake_puzzle_hash,puzzle_hash,amount,stake_type,coefficient,expiration FROM "
                "stake_record INDEXED BY stake_puzzle_hash WHERE stake_puzzle_hash=? AND is_stake_farm=1 "
                "AND confirmed_index<? AND expiration>?", (stake_puzzle_hash, height, timestamp,),
            ) as cursor:
                records: List[StakeRecordThin] = []
                puzzle_hashes: set[bytes32] = set()

                for row in await cursor.fetchall():
                    puzzle_hash = bytes32(row[1])
                    if len(puzzle_hashes) >= STAKE_FARM_COUNT and puzzle_hash not in puzzle_hashes:
                        continue
                    puzzle_hashes.add(puzzle_hash)
                    records.append(StakeRecordThin(
                        bytes32(row[0]),
                        puzzle_hash,
                        uint64(int(row[2])),
                        row[3],
                        True,
                        float(row[4]),
                        row[5],
                    ))
                self.stake_farm_cache.put(stake_key, records)
                return records

    async def get_stake_lock_records_thin(
            self, start: uint64, end: uint64
    ) -> List[StakeRecordThin]:
        stake_key = bytes32(start.to_bytes(16, "big") + end.to_bytes(16, "big"))
        stake_list: Optional[List[StakeRecordThin]] = self.stake_lock_cache.get(stake_key)
        if stake_list is not None:
            return stake_list

        async with self.db_wrapper.reader_no_transaction() as conn:
            async with conn.execute(
                "SELECT stake_puzzle_hash,puzzle_hash,amount,stake_type,coefficient,expiration FROM "
                "stake_record INDEXED BY stake_expiration WHERE is_stake_farm=0 AND expiration>? "
                "AND expiration%86400>=? AND expiration%86400<?",
                (end, start % 86400 + 300, end % 86400 + 300,),
            ) as cursor:
                records: List[StakeRecordThin] = []
                for row in await cursor.fetchall():
                    records.append(StakeRecordThin(
                        bytes32(row[0]),
                        bytes32(row[1]),
                        uint64(int(row[2])),
                        row[3],
                        False,
                        float(row[4]),
                        row[5],
                    ))
                self.stake_lock_cache.put(stake_key, records)
                return records
