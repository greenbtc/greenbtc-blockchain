from __future__ import annotations

from dataclasses import dataclass
from typing import List

from greenbtc.consensus.block_rewards import MOJO_PER_GBTC
from greenbtc.util.ints import uint16, uint64, uint32
from greenbtc.util.streamable import Streamable, streamable

STAKE_PER_COEFFICIENT = 10 ** 17

STAKE_FARM_COUNT = 128
STAKE_FARM_MIN = 100 * MOJO_PER_GBTC
STAKE_FARM_PREFIX = "dpos:gbtc:"

STAKE_LOCK_MIN = 100 * MOJO_PER_GBTC


@streamable
@dataclass(frozen=True)
class ProofOfStake(Streamable):
    height: uint32
    coefficient: uint64


@streamable
@dataclass(frozen=True)
class StakeValue(Streamable):
    time_lock: uint64
    coefficient: str

    def reward_amount(self, amount: uint64) -> int:
        return int(int(amount) * float(self.coefficient) * MOJO_PER_GBTC)


STAKE_FARM_LIST: List[StakeValue] = [
    StakeValue(86400 * 3, "1.0"),
    StakeValue(86400 * 10, "1.1"),
    StakeValue(86400 * 30, "1.2"),
    StakeValue(86400 * 90, "1.4"),
    StakeValue(86400 * 180, "1.6"),
    StakeValue(86400 * 365, "2.0"),
    StakeValue(86400 * 730, "2.5"),
    StakeValue(86400 * 1095, "3.0"),
    StakeValue(86400 * 1825, "4.0"),
]


STAKE_LOCK_LIST: List[StakeValue] = [
    StakeValue(86400 * 3, "0.0002"),
    StakeValue(86400 * 30, "0.00025"),
    StakeValue(86400 * 90, "0.0003"),
    StakeValue(86400 * 180, "0.0004"),
    StakeValue(86400 * 365, "0.0005"),
    StakeValue(86400 * 730, "0.00053"),
    StakeValue(86400 * 1095, "0.00055"),
    StakeValue(86400 * 1825, "0.00058"),
    StakeValue(86400 * 3650, "0.00062"),
    StakeValue(86400 * 7300, "0.00066"),
    StakeValue(86400 * 10950, "0.0007"),
]


def get_stake_value(stake_type: uint16, is_stake_farm: bool) -> StakeValue:
    value = STAKE_FARM_LIST if is_stake_farm else STAKE_LOCK_LIST

    if 0 <= stake_type < len(value):
        return value[stake_type]
    return StakeValue(0, "0")
