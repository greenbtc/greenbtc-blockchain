from typing import KeysView, Generator

SERVICES_FOR_GROUP = {
    "all": (
        "greenbtc_harvester greenbtc_timelord_launcher greenbtc_timelord greenbtc_farmer "
        "greenbtc_full_node greenbtc_wallet greenbtc_data_layer greenbtc_data_layer_http"
    ).split(),
    # TODO: should this be `data_layer`?
    "data": "greenbtc_wallet greenbtc_data_layer".split(),
    "data_layer_http": "greenbtc_data_layer_http".split(),
    "node": "greenbtc_full_node".split(),
    "harvester": "greenbtc_harvester".split(),
    "farmer": "greenbtc_harvester greenbtc_farmer greenbtc_full_node greenbtc_wallet".split(),
    "farmer-no-wallet": "greenbtc_harvester greenbtc_farmer greenbtc_full_node".split(),
    "farmer-only": "greenbtc_farmer".split(),
    "timelord": "greenbtc_timelord_launcher greenbtc_timelord greenbtc_full_node".split(),
    "timelord-only": "greenbtc_timelord".split(),
    "timelord-launcher-only": "greenbtc_timelord_launcher".split(),
    "wallet": "greenbtc_wallet".split(),
    "introducer": "greenbtc_introducer".split(),
    "simulator": "greenbtc_full_node_simulator".split(),
    "crawler": "greenbtc_crawler".split(),
    "seeder": "greenbtc_crawler greenbtc_seeder".split(),
    "seeder-only": "greenbtc_seeder".split(),
}


def all_groups() -> KeysView[str]:
    return SERVICES_FOR_GROUP.keys()


def services_for_groups(groups) -> Generator[str, None, None]:
    for group in groups:
        for service in SERVICES_FOR_GROUP[group]:
            yield service


def validate_service(service: str) -> bool:
    return any(service in _ for _ in SERVICES_FOR_GROUP.values())
