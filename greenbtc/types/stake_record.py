from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


from greenbtc.consensus.block_rewards import calculate_stake_farm_reward
from greenbtc.consensus.coinbase import create_stake_farm_reward_coin, create_stake_lock_reward_coin
from greenbtc.consensus.constants import ConsensusConstants
from greenbtc.types.blockchain_format.coin import Coin
from greenbtc.types.blockchain_format.sized_bytes import bytes32
from greenbtc.util.ints import uint32, uint64, uint16
from greenbtc.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class StakeRecord(Streamable):
    name: bytes32
    amount: uint64
    confirmed_block_index: uint32
    spent_block_index: uint32
    stake_puzzle_hash: bytes32
    puzzle_hash: bytes32
    stake_type: uint16
    is_stake_farm: bool
    coefficient: str
    expiration: uint64


@streamable
@dataclass(frozen=True)
class StakeRecordThin(Streamable):
    stake_puzzle_hash: bytes32
    puzzle_hash: bytes32
    amount: uint64
    stake_type: uint16
    is_stake_farm: bool
    coefficient: str
    expiration: uint64


def create_stake_farm_rewards(
    constants: ConsensusConstants,
    records: Dict[bytes32, int],
    height: uint32,
) -> List[Coin]:
    stake_rewards: List[Coin] = []
    reward_amount = calculate_stake_farm_reward(height)
    sum_amount = sum(records[puzzle_hash] for puzzle_hash in records)
    balance = reward_amount
    total = len(records) - 1
    for index, puzzle_hash in enumerate(records.keys()):
        if index == total:
            amount = balance
        else:
            amount = int(records[puzzle_hash] * reward_amount / sum_amount)
            balance -= amount
        stake_coin = create_stake_farm_reward_coin(
            height,
            puzzle_hash,
            uint64(amount),
            constants.GENESIS_CHALLENGE,
        )
        stake_rewards.append(stake_coin)
    return stake_rewards


def create_stake_lock_rewards(
    constants: ConsensusConstants,
    records: Dict[bytes32, int],
    height: uint32,
) -> List[Coin]:
    stake_rewards: List[Coin] = []
    for puzzle_hash in records:
        stake_coin = create_stake_lock_reward_coin(
            height,
            puzzle_hash,
            uint64(records[puzzle_hash]),
            constants.GENESIS_CHALLENGE,
        )
        stake_rewards.append(stake_coin)
    return stake_rewards
