from __future__ import annotations

from dataclasses import dataclass

from greenbtc.types.blockchain_format.sized_bytes import bytes32
from greenbtc.util.ints import uint32
from greenbtc.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class PoolTarget(Streamable):
    puzzle_hash: bytes32
    max_height: uint32  # A max height of 0 means it is valid forever
