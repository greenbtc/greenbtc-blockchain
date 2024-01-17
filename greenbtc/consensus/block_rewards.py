from __future__ import annotations

from greenbtc.util.ints import uint32, uint64

# 1 GreenBTC coin = 1,000,000,000,000 = 1 trillion mojo.
MOJO_PER_GBTC = 1000000000000


def calculate_pool_reward(height: uint32) -> uint64:
    """
    Returns the pool reward at a certain block height. The pool earns 7/8 of the reward in each block. If the farmer
    is solo farming, they act as the pool, and therefore earn the entire block reward.
    These halving events will not be hit at the exact times
    (3 years, etc), due to fluctuations in difficulty. They will likely come early, if the network space and VDF
    rates increase continuously.
    """

    if height == 0:
        return uint64(int((7 / 8) * 3000000 * MOJO_PER_GBTC))
    elif height < 1000000:
        return uint64(int((7 / 8) * 1 * MOJO_PER_GBTC))
    elif height < 2000000:
        return uint64(int((7 / 8) * 0.6 * MOJO_PER_GBTC))
    elif height < 10000000:
        return uint64(int((7 / 8) * 0.4 * MOJO_PER_GBTC))
    elif height < 20000000:
        return uint64(int((7 / 8) * 0.2 * MOJO_PER_GBTC))
    elif height < 30000000:
        return uint64(int((7 / 8) * 0.1 * MOJO_PER_GBTC))
    elif height < 40000000:
        return uint64(int((7 / 8) * 0.05 * MOJO_PER_GBTC))
    elif height < 50000000:
        return uint64(int((7 / 8) * 0.02 * MOJO_PER_GBTC))
    else:
        return uint64(int((7 / 8) * 0.01 * MOJO_PER_GBTC))


def calculate_base_farmer_reward(height: uint32) -> uint64:
    """
    Returns the base farmer reward at a certain block height.
    The base fee reward is 1/8 of total block reward

    Returns the coinbase reward at a certain block height. These halving events will not be hit at the exact times
    (3 years, etc), due to fluctuations in difficulty. They will likely come early, if the network space and VDF
    rates increase continuously.
    """
    if height == 0:
        return uint64(int((1 / 8) * 3000000 * MOJO_PER_GBTC))
    elif height < 1000000:
        return uint64(int((1 / 8) * 1 * MOJO_PER_GBTC))
    elif height < 2000000:
        return uint64(int((1 / 8) * 0.6 * MOJO_PER_GBTC))
    elif height < 10000000:
        return uint64(int((1 / 8) * 0.4 * MOJO_PER_GBTC))
    elif height < 20000000:
        return uint64(int((1 / 8) * 0.2 * MOJO_PER_GBTC))
    elif height < 30000000:
        return uint64(int((1 / 8) * 0.1 * MOJO_PER_GBTC))
    elif height < 40000000:
        return uint64(int((1 / 8) * 0.05 * MOJO_PER_GBTC))
    elif height < 50000000:
        return uint64(int((1 / 8) * 0.02 * MOJO_PER_GBTC))
    else:
        return uint64(int((1 / 8) * 0.01 * MOJO_PER_GBTC))


def calculate_stake_farm_reward(height: uint32) -> uint64:
    """
    Returns the stake farm reward at a certain block height.
    The base fee reward is 400% of total block reward

    Returns the coinbase reward at a certain block height. These halving events will not be hit at the exact times
    , due to fluctuations in difficulty. They will likely come early, if the network space and VDF
    rates increase continuously.
    """
    if height < 2000000:
        return uint64(0)
    elif height < 10000000:
        return uint64(int(5 * 0.4 * MOJO_PER_GBTC))
    elif height < 20000000:
        return uint64(int(5 * 0.2 * MOJO_PER_GBTC))
    elif height < 30000000:
        return uint64(int(5 * 0.1 * MOJO_PER_GBTC))
    elif height < 40000000:
        return uint64(int(5 * 0.05 * MOJO_PER_GBTC))
    elif height < 50000000:
        return uint64(int(5 * 0.02 * MOJO_PER_GBTC))
    else:
        return uint64(int(5 * 0.01 * MOJO_PER_GBTC))
