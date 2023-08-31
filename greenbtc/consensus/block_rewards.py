from __future__ import annotations

from greenbtc.util.ints import uint32, uint64

# 1 GreenBTC coin = 1,000,000,000,000 = 1 trillion mojo.
_mojo_per_greenbtc = 1000000000000


def calculate_pool_reward(height: uint32) -> uint64:
    """
    Returns the pool reward at a certain block height. The pool earns 7/8 of the reward in each block. If the farmer
    is solo farming, they act as the pool, and therefore earn the entire block reward.
    These halving events will not be hit at the exact times
    (1 month, etc), due to fluctuations in difficulty. They will likely come early, if the network space and VDF
    rates increase continuously.
    """

    if height == 0:
        return uint64(int((7 / 8) * 3000000 * _mojo_per_greenbtc))
    elif height < 1000000:
        return uint64(int((7 / 8) * 1 * _mojo_per_greenbtc))
    elif height < 2000000:
        return uint64(int((7 / 8) * 0.6 * _mojo_per_greenbtc))
    elif height < 3000000:
        return uint64(int((7 / 8) * 0.4 * _mojo_per_greenbtc))
    elif height < 4000000:
        return uint64(int((7 / 8) * 0.2 * _mojo_per_greenbtc))
    elif height < 20000000:
        return uint64(int((7 / 8) * 0.1 * _mojo_per_greenbtc))
    else:
        return uint64(int((7 / 8) * 0.05 * _mojo_per_greenbtc))


def calculate_base_farmer_reward(height: uint32) -> uint64:
    """
    Returns the base farmer reward at a certain block height.
    The base fee reward is 1/8 of total block reward

    Returns the coinbase reward at a certain block height. These halving events will not be hit at the exact times
    (1 month, etc), due to fluctuations in difficulty. They will likely come early, if the network space and VDF
    rates increase continuously.
    """
    if height == 0:
        return uint64(int((1 / 8) * 3000000 * _mojo_per_greenbtc))
    elif height < 1000000:
        return uint64(int((1 / 8) * 1 * _mojo_per_greenbtc))
    elif height < 2000000:
        return uint64(int((1 / 8) * 0.6 * _mojo_per_greenbtc))
    elif height < 3000000:
        return uint64(int((1 / 8) * 0.4 * _mojo_per_greenbtc))
    elif height < 4000000:
        return uint64(int((1 / 8) * 0.2 * _mojo_per_greenbtc))
    elif height < 20000000:
        return uint64(int((1 / 8) * 0.1 * _mojo_per_greenbtc))
    else:
        return uint64(int((1 / 8) * 0.05 * _mojo_per_greenbtc))

