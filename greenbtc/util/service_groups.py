from __future__ import annotations

from typing import Generator, Iterable, KeysView

SERVICES_FOR_GROUP = {
    "all": [
        "greenbtc_harvester",
        "greenbtc_timelord_launcher",
        "greenbtc_timelord",
        "greenbtc_farmer",
        "greenbtc_full_node",
        "greenbtc_wallet",
        "greenbtc_data_layer",
        "greenbtc_data_layer_http",
    ],
    # TODO: should this be `data_layer`?
    "data": ["greenbtc_wallet", "greenbtc_data_layer"],
    "data_layer_http": ["greenbtc_data_layer_http"],
    "node": ["greenbtc_full_node"],
    "harvester": ["greenbtc_harvester"],
    "farmer": ["greenbtc_harvester", "greenbtc_farmer", "greenbtc_full_node", "greenbtc_wallet"],
    "farmer-no-wallet": ["greenbtc_harvester", "greenbtc_farmer", "greenbtc_full_node"],
    "farmer-only": ["greenbtc_farmer"],
    "timelord": ["greenbtc_timelord_launcher", "greenbtc_timelord", "greenbtc_full_node"],
    "timelord-only": ["greenbtc_timelord"],
    "timelord-launcher-only": ["greenbtc_timelord_launcher"],
    "wallet": ["greenbtc_wallet"],
    "introducer": ["greenbtc_introducer"],
    "simulator": ["greenbtc_full_node_simulator"],
    "crawler": ["greenbtc_crawler"],
    "seeder": ["greenbtc_crawler", "greenbtc_seeder"],
    "seeder-only": ["greenbtc_seeder"],
}


def all_groups() -> KeysView[str]:
    return SERVICES_FOR_GROUP.keys()


def services_for_groups(groups: Iterable[str]) -> Generator[str, None, None]:
    for group in groups:
        yield from SERVICES_FOR_GROUP[group]


def validate_service(service: str) -> bool:
    return any(service in _ for _ in SERVICES_FOR_GROUP.values())
