from __future__ import annotations

import asyncio
import time
from decimal import Decimal
from typing import Optional

from greenbtc.cmds.cmds_util import transaction_status_msg, transaction_submitted_msg, get_wallet_client
from greenbtc.cmds.units import units
from greenbtc.rpc.wallet_rpc_client import WalletRpcClient
from greenbtc.util.ints import uint64
from greenbtc.wallet.util.wallet_types import WalletType


async def get_wallet_type(wallet_id: int, wallet_client: WalletRpcClient) -> WalletType:
    summaries_response = await wallet_client.get_wallets()
    for summary in summaries_response:
        summary_id: int = summary["id"]
        summary_type: int = summary["type"]
        if wallet_id == summary_id:
            return WalletType(summary_type)

    raise LookupError(f"Wallet ID not found: {wallet_id}")


async def staking_info(wallet_rpc_port: Optional[int], fp: Optional[int]) -> None:
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, _):
        balance, address = await wallet_client.staking_info(fingerprint)
        greenbtc = balance / units["greenbtc"]
        print(f"Staking balance: {greenbtc}")
        print(f"Staking address: {address}")


async def staking_send(wallet_rpc_port: Optional[int], wallet_id: int, fp: Optional[int], amount: Decimal) -> None:
    if amount == 0:
        print("You can not staking an empty transaction")
        return
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, _):
        try:
            typ = await get_wallet_type(wallet_id=wallet_id, wallet_client=wallet_client)
            if typ != WalletType.STANDARD_WALLET:
                print("Only standard wallet wallets")
                return
        except LookupError:
            print(f"Wallet id: {wallet_id} not found.")
            return

        print("Submitting staking transaction...")
        res = await wallet_client.staking_send(wallet_id, uint64(int(amount * units["greenbtc"])), fingerprint)

        tx_id = res.name
        start = time.time()
        while time.time() - start < 10:
            await asyncio.sleep(0.1)
            tx = await wallet_client.get_transaction(1, tx_id)
            if len(tx.sent_to) > 0:
                print(transaction_submitted_msg(tx))
                print(transaction_status_msg(fingerprint, tx_id))
                return None

        print("Staking transaction not yet submitted to nodes")
        print(f"To get status, use command: greenbtc wallet get_transaction -f {fingerprint} -tx 0x{tx_id}")


async def staking_withdraw(
    wallet_rpc_port: Optional[int], fp: Optional[int], wallet_id: int, amount: Decimal, address: str
) -> None:
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, _):
        try:
            typ = await get_wallet_type(wallet_id=wallet_id, wallet_client=wallet_client)
            if typ != WalletType.STANDARD_WALLET:
                print("Only standard wallet wallets")
                return
        except LookupError:
            print(f"Wallet id: {wallet_id} not found.")
            return

        print("Submitting withdraw staking transaction...")
        res = await wallet_client.staking_withdraw(
            wallet_id, address, uint64(int(amount * units["greenbtc"])), fingerprint
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

        print("Withdraw staking transaction not yet submitted to nodes")
        print(f"To get status, use command: greenbtc wallet get_transaction -f {fingerprint} -tx 0x{tx_id}")


async def find_pool_nft(
    wallet_rpc_port: Optional[int],
    fp: Optional[int],
    launcher_id: str,
    contract_address: str
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
    contract_address: str
) -> None:
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, _):
        response = await wallet_client.recover_pool_nft(launcher_id, contract_address)
        address = response["contract_address"]
        status = response["status"]
        amount = response["amount"] / units["greenbtc"]
        print(f"Contract Address: {address}")
        print(f"Record Amount: {amount} GBTC")
        print(f"Status: {status}")
