from __future__ import annotations

from chia_rs import G1Element

from greenbtc.types.blockchain_format.coin import Coin
from greenbtc.types.blockchain_format.sized_bytes import bytes32
from greenbtc.util.ints import uint32, uint64
from greenbtc.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import puzzle_hash_for_pk


def create_puzzlehash_for_pk(pub_key: G1Element) -> bytes32:
    return puzzle_hash_for_pk(pub_key)


def pool_parent_id(block_height: uint32, genesis_challenge: bytes32) -> bytes32:
    return bytes32(genesis_challenge[:16] + block_height.to_bytes(16, "big"))


def farmer_parent_id(block_height: uint32, genesis_challenge: bytes32) -> bytes32:
    return bytes32(genesis_challenge[16:] + block_height.to_bytes(16, "big"))


def stake_farm_reward_parent_id(block_height: uint32, genesis_challenge: bytes32) -> bytes32:
    return bytes32(genesis_challenge[8:24] + block_height.to_bytes(16, "big"))


def stake_lock_reward_parent_id(block_height: uint32, genesis_challenge: bytes32) -> bytes32:
    return bytes32(genesis_challenge[12:28] + block_height.to_bytes(16, "big"))


def create_pool_coin(block_height: uint32, puzzle_hash: bytes32, reward: uint64, genesis_challenge: bytes32) -> Coin:
    parent_id = pool_parent_id(block_height, genesis_challenge)
    return Coin(parent_id, puzzle_hash, reward)


def create_farmer_coin(block_height: uint32, puzzle_hash: bytes32, reward: uint64, genesis_challenge: bytes32) -> Coin:
    parent_id = farmer_parent_id(block_height, genesis_challenge)
    return Coin(parent_id, puzzle_hash, reward)


def create_stake_farm_reward_coin(
    block_height: uint32, puzzle_hash: bytes32, reward: uint64, genesis_challenge: bytes32
) -> Coin:
    parent_id = stake_farm_reward_parent_id(block_height, genesis_challenge)
    return Coin(parent_id, puzzle_hash, reward)


def create_stake_lock_reward_coin(
    block_height: uint32, puzzle_hash: bytes32, reward: uint64, genesis_challenge: bytes32
) -> Coin:
    parent_id = stake_lock_reward_parent_id(block_height, genesis_challenge)
    return Coin(parent_id, puzzle_hash, reward)
