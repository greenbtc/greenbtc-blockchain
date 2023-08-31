import asyncio
from decimal import Decimal
from typing import Optional

import click


@click.group("staking", short_help="Manage your staking")
@click.pass_context
def staking_cmd(ctx: click.Context) -> None:
    pass


@staking_cmd.command("info", short_help="Query staking info")
@click.option(
    "-wp",
    "--wallet-rpc-port",
    help="Set the port where the Wallet is hosting the RPC interface. See the rpc_port under wallet in config.yaml",
    type=int,
    default=None,
)
@click.option("-f", "--fingerprint", help="Set the fingerprint to specify which wallet to use", type=int)
def staking_info(
    wallet_rpc_port: Optional[int],
    fingerprint: int,
) -> None:
    from .staking_funcs import staking_info

    asyncio.run(
        staking_info(
            wallet_rpc_port=wallet_rpc_port,
            fp=fingerprint,
        )
    )


@staking_cmd.command("send", short_help="Send greenbtc to staking address")
@click.option(
    "-wp",
    "--wallet-rpc-port",
    help="Set the port where the Wallet is hosting the RPC interface. See the rpc_port under wallet in config.yaml",
    type=int,
    default=None,
)
@click.option("-f", "--fingerprint", help="Set the fingerprint to specify which wallet to use", type=int)
@click.option("-i", "--id", help="Id of the wallet to use", type=int, default=1, show_default=True, required=True)
@click.option("-a", "--amount", help="How much greenbtc to send, in GBTC", type=str, required=True)
def staking_send_cmd(
    wallet_rpc_port: Optional[int],
    fingerprint: int,
    id: int,
    amount: str,
) -> None:
    from .staking_funcs import staking_send

    asyncio.run(
        staking_send(
            wallet_rpc_port=wallet_rpc_port,
            fp=fingerprint,
            wallet_id=id,
            amount=Decimal(amount),
        )
    )


@staking_cmd.command("withdraw", short_help="Withdraw staking greenbtc")
@click.option(
    "-wp",
    "--wallet-rpc-port",
    help="Set the port where the Wallet is hosting the RPC interface. See the rpc_port under wallet in config.yaml",
    type=int,
    default=None,
)
@click.option("-f", "--fingerprint", help="Set the fingerprint to specify which wallet to use", type=int)
@click.option("-i", "--id", help="Id of the wallet to use", type=int, default=1, show_default=True, required=True)
@click.option(
    "-a",
    "--amount",
    help="withdraw staking GBTC, 0 will withdraw all staking",
    type=str,
    default="0",
    show_default=True
)
@click.option("-t", "--address", help="staking withdraw address", type=str, default="", show_default=True)
def staking_withdraw_cmd(
    wallet_rpc_port: Optional[int],
    fingerprint: int,
    id: int,
    amount: str,
    address: str,
) -> None:
    from .staking_funcs import staking_withdraw

    asyncio.run(
        staking_withdraw(
            wallet_rpc_port=wallet_rpc_port,
            fp=fingerprint,
            wallet_id=id,
            amount=Decimal(amount),
            address=address,
        )
    )
