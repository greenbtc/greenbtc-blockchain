from __future__ import annotations

import asyncio
import sys
import time
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List

from greenbtc.cmds.cmds_util import transaction_status_msg, transaction_submitted_msg, get_wallet_client
from greenbtc.cmds.units import units
from greenbtc.rpc.wallet_rpc_client import WalletRpcClient
from greenbtc.types.blockchain_format.sized_bytes import bytes32
from greenbtc.types.stake_value import STAKE_FARM_LIST, STAKE_LOCK_LIST
from greenbtc.util.bech32m import encode_puzzle_hash
from greenbtc.util.config import selected_network_address_prefix
from greenbtc.util.errors import CliRpcConnectionError
from greenbtc.util.ints import uint64
from greenbtc.wallet.transaction_record import TransactionRecord
from greenbtc.wallet.transaction_sorting import SortKey
from greenbtc.wallet.util.query_filter import TransactionTypeFilter, HashFilter
from greenbtc.wallet.util.transaction_type import TransactionType
from greenbtc.wallet.util.wallet_types import WalletType
from greenbtc.wallet.wallet_coin_store import GetCoinRecords

transaction_type_descriptions = {
    TransactionType.OUTGOING_STAKE_FARM: "outgoing stake farm",
    TransactionType.INCOMING_STAKE_FARM_RECEIVE: "stake farm",
    TransactionType.STAKE_FARM_WITHDRAW: "withdraw/stake farm",
    TransactionType.STAKE_FARM_REWARD: "stake farm reward",
    TransactionType.INCOMING_STAKE_LOCK_RECEIVE: "stake lock",
    TransactionType.STAKE_LOCK_WITHDRAW: "withdraw/stake lock",
    TransactionType.STAKE_LOCK_REWARD: "stake lock reward",
}


def transaction_description_from_type(tx: TransactionRecord) -> str:
    return transaction_type_descriptions.get(TransactionType(tx.type), "(unknown reason)")


async def get_wallet_type(wallet_id: int, wallet_client: WalletRpcClient) -> WalletType:
    summaries_response = await wallet_client.get_wallets()
    for summary in summaries_response:
        summary_id: int = summary["id"]
        summary_type: int = summary["type"]
        if wallet_id == summary_id:
            return WalletType(summary_type)

    raise LookupError(f"Wallet ID not found: {wallet_id}")


def check_unusual_transaction(amount: Decimal, fee: Decimal) -> bool:
    return fee >= amount


def print_transaction(
    tx: TransactionRecord,
    verbose: bool,
    address_prefix: str,
    coin_record: Optional[Dict[str, Any]] = None,
) -> None:  # pragma: no cover
    if verbose:
        print(tx)
    else:
        greenbtc_amount = Decimal(int(tx.amount)) / units["greenbtc"]
        to_address = bytes32.from_hexstr(coin_record["metadata"]["stake_puzzle_hash"])
        time_lock = coin_record["metadata"]["time_lock"]
        print(f"Transaction {tx.name}")
        description = transaction_description_from_type(tx)
        print(f"Amount {description}: {greenbtc_amount} {address_prefix.upper()}")
        print(f"Stake address: {encode_puzzle_hash(to_address, address_prefix)}")
        print(f"Datetime at: {datetime.fromtimestamp(tx.created_at_time).strftime('%Y-%m-%d %H:%M:%S')} - "
              f"{datetime.fromtimestamp(tx.created_at_time + time_lock).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Stake {'in' if tx.created_at_time + time_lock > time.time() else 'exp'}")
        print("")


async def stake_transactions(
        *,
        wallet_rpc_port: Optional[int],
        fp: Optional[int],
        wallet_id: int,
        verbose: int,
        paginate: Optional[bool],
        offset: int,
        limit: int,
        sort_key: SortKey,
        reverse: bool,
) -> None:  # pragma: no cover
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, config):
        if paginate is None:
            paginate = sys.stdout.isatty()
        type_filter = (
            TransactionTypeFilter.include([
                TransactionType.INCOMING_STAKE_FARM_RECEIVE,
                TransactionType.INCOMING_STAKE_LOCK_RECEIVE,
            ])
        )
        txs: List[TransactionRecord] = await wallet_client.get_transactions(
            wallet_id, start=offset, end=(offset + limit), sort_key=sort_key, reverse=reverse, type_filter=type_filter
        )

        address_prefix = selected_network_address_prefix(config)
        if len(txs) == 0:
            print("There are no stake transactions to this address")

        skipped = 0
        num_per_screen = 5 if paginate else len(txs)
        for i in range(0, len(txs), num_per_screen):
            for j in range(0, num_per_screen):
                if i + j + skipped >= len(txs):
                    break
                coin_record: Optional[Dict[str, Any]] = None
                coin_records = await wallet_client.get_coin_records(
                    GetCoinRecords(coin_id_filter=HashFilter.include([txs[i + j + skipped].additions[0].name()]))
                )
                if len(coin_records["coin_records"]) > 0:
                    coin_record = coin_records["coin_records"][0]
                else:
                    j -= 1
                    skipped += 1
                    continue
                print_transaction(
                    txs[i + j + skipped],
                    verbose=(verbose > 0),
                    address_prefix=address_prefix,
                    coin_record=coin_record,
                )
            if i + num_per_screen >= len(txs):
                return None
            print("Press q to quit, or c to continue")
            while True:
                entered_key = sys.stdin.read(1)
                if entered_key == "q":
                    return None
                elif entered_key == "c":
                    break


async def stake_info(
        wallet_rpc_port: Optional[int], fp: Optional[int], stake_category: str
) -> None:
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, _):
        is_stake_farm = stake_category == "farm"
        response = await wallet_client.stake_info(fingerprint, is_stake_farm)
        print(f"Stake Category: "+stake_category)
        if is_stake_farm:
            print(f"Stake Balance: {response['balance'] / units['greenbtc']}")
            print(f"Stake Balance Other: {response['balance_other'] / units['greenbtc']}")
            print(f"Stake Balance Income: {response['balance_income'] / units['greenbtc']}")
            print(f"Stake Balance 24H Exp: {response['balance_exp'] / units['greenbtc']}")
            print(f"Stake Reward: {response['stake_reward'] / units['greenbtc']}")
            print(f"Stake Address: {response['address']}")
        else:
            print(f"Stake Balance: {response['balance'] / units['greenbtc']}")
            print(f"Stake Balance 24H Exp: {response['balance_exp'] / units['greenbtc']}")
            print(f"Stake Reward: {response['stake_reward'] / units['greenbtc']}")


async def stake_send(
    wallet_rpc_port: Optional[int],
    fp: Optional[int],
    wallet_id: int,
    amount: int,
    fee: Decimal,
    address: str,
    stake_type: Optional[int],
    stake_category: str,
) -> None:
    if amount == 0:
        print("You can not stake an empty transaction")
        return

    selected_stake_type: int = 0
    is_stake_farm = stake_category == "farm"
    value_list = STAKE_FARM_LIST if is_stake_farm else STAKE_LOCK_LIST
    if stake_type is not None:
        if stake_type < 0 or stake_type >= len(value_list):
            raise CliRpcConnectionError("Invalid stake type")
        selected_stake_type = stake_type
    else:
        print()
        print(f"Stake Category: {stake_category}, Stake Types:")
        for i, value in enumerate(value_list):
            key_index_str = f"{(str(i) + ')'):<4}"
            key_index_str += "*" if i == 0 else " "
            print(
                f"{key_index_str:<{5}} "
                f"{int(value.time_lock / 86400)} Days "
                f"({value.coefficient if is_stake_farm else str(float(Decimal(value.coefficient) * 10000))+'‱'})"
            )
        val = None
        prompt: str = (
            f"Choose a stake type [0-{len(value_list) - 1}]"
            f" ('q' to quit, or Enter to use 0): "
        )
        while val is None:
            val = input(prompt)
            if val == "q":
                raise CliRpcConnectionError("No stake type Selected")
            elif val == "":
                selected_stake_type = 0
                break
            elif not val.isdigit():
                val = None
            else:
                index = int(val)
                if index < 0 or index >= len(value_list):
                    print("Invalid stake type")
                    val = None
                    continue
                else:
                    selected_stake_type = index
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, _):
        if check_unusual_transaction(Decimal(amount), fee):
            print(
                f"A transaction of amount {amount} and fee {fee} is unusual.\n"
            )
            return

        final_amount = int(amount * units["greenbtc"])
        if not (final_amount / units["greenbtc"]).is_integer():
            print(
                f"A transaction of amount {amount} must be a positive integer.\n"
            )
            return
        try:
            typ = await get_wallet_type(wallet_id=wallet_id, wallet_client=wallet_client)
            if typ != WalletType.STANDARD_WALLET:
                print("Only standard wallet wallets")
                return
        except LookupError:
            print(f"Wallet id: {wallet_id} not found.")
            return

        print("Submitting stake transaction...")
        final_fee: uint64 = uint64(int(fee * units["greenbtc"]))  # fees are always in GBTC mojos
        res = await wallet_client.stake_send(
            wallet_id,
            selected_stake_type,
            is_stake_farm,
            address,
            uint64(final_amount),
            final_fee,
        )

        tx_id = res.name
        start = time.time()
        while time.time() - start < 10:
            await asyncio.sleep(0.1)
            tx = await wallet_client.get_transaction(1, tx_id)
            if len(tx.sent_to) > 0:
                print(transaction_submitted_msg(tx))
                print(transaction_status_msg(fingerprint, tx_id))
                return None

        print("Stake transaction not yet submitted to nodes")
        print(f"To get status, use command: greenbtc wallet get_transaction -f {fingerprint} -tx 0x{tx_id}")


#
#
# async def spend_stake_coins(
#     *, wallet_rpc_port: Optional[int], fp: Optional[int], fee: Decimal, tx_ids_str: str
# ) -> None:  # pragma: no cover
#     async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, _, _):
#         tx_ids = []
#         for tid in tx_ids_str.split(","):
#             tx_ids.append(bytes32.from_hexstr(tid))
#         if len(tx_ids) == 0:
#             print("Transaction ID is required.")
#             return
#         if fee < 0:
#             print("Batch fee cannot be negative.")
#             return
#         response = await wallet_client.spend_stake_coins(tx_ids, int(fee * units["greenbtc"]))
#         print(str(response))


async def find_pool_nft(
        wallet_rpc_port: Optional[int],
        fp: Optional[int],
        launcher_id: str,
        contract_address: str,
) -> None:
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, _):
        response = await wallet_client.find_pool_nft(launcher_id, contract_address)
        address = response["contract_address"]
        total_amount = response["total_amount"] / units["greenbtc"]
        record_amount = response["record_amount"] / units["greenbtc"]
        balance_amount = response["balance_amount"] / units["greenbtc"]
        print(f"Contract Address: {address}")
        print(f"Total Amount: {total_amount} GBTC")
        print(f"Balance Amount: {balance_amount} GBTC")
        print(f"Record Amount: {record_amount} GBTC")


async def recover_pool_nft(
        wallet_rpc_port: Optional[int],
        fp: Optional[int],
        launcher_id: str,
        contract_address: str,
        fee: Decimal,
) -> None:
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, _):
        final_fee: uint64 = uint64(int(fee * units["greenbtc"]))
        response = await wallet_client.recover_pool_nft(launcher_id, contract_address, final_fee)
        address = response["contract_address"]
        status = response["status"]
        amount = response["amount"] / units["greenbtc"]
        print(f"Contract Address: {address}")
        print(f"Record Amount: {amount} GBTC")
        print(f"Status: {status}")


async def stake_withdraw_old(
    wallet_rpc_port: Optional[int],
    fp: Optional[int],
    wallet_id: int,
    amount: Decimal,
) -> None:
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, _):
        final_amount = int(amount * units["greenbtc"])
        if not (final_amount / units["greenbtc"]).is_integer():
            print(
                f"A transaction of amount {amount} must be a positive integer.\n"
            )
            return
        try:
            typ = await get_wallet_type(wallet_id=wallet_id, wallet_client=wallet_client)
            if typ != WalletType.STANDARD_WALLET:
                print("Only standard wallet wallets")
                return
        except LookupError:
            print(f"Wallet id: {wallet_id} not found.")
            return

        print("Submitting withdraw old stake transaction...")
        res = await wallet_client.stake_withdraw_old(
            wallet_id,
            uint64(final_amount),
        )

        tx_id = res.name
        start = time.time()
        while time.time() - start < 10:
            await asyncio.sleep(0.1)
            tx = await wallet_client.get_transaction(1, tx_id)
            if len(tx.sent_to) > 0:
                print(transaction_submitted_msg(tx))
                print(transaction_status_msg(fingerprint, tx_id))
                return None

        print("Withdraw old stake transaction not yet submitted to nodes")
        print(f"To get status, use command: greenbtc wallet get_transaction -f {fingerprint} -tx 0x{tx_id}")
