# greenbtc-blockchain (GBTC)
![IMG_4734](https://github.com/greenbtc/greenbtc-blockchain-gui/raw/main/packages/gui/src/assets/img/greenbtc.png)

GreenBTC(GBTC) is a modern cryptocurrency built from scratch, designed to be efficient, decentralized, and secure. Here are some of the features and benefits:
* [Proof of space and time](https://docs.google.com/document/d/1tmRIb7lgi4QfKkNaxuKOBHRmwbVlGL4f7EsBDr_5xZE/edit) based consensus which allows anyone to farm with commodity hardware
* Very easy to use full node and farmer GUI and cli (thousands of nodes active on mainnet)
* Simplified UTXO based transaction model, with small on-chain state
* Lisp-style Turing-complete functional [programming language](https://chialisp.com/) for money related use cases
* BLS keys and aggregate signatures (only one signature per block)
* [Pooling protocol](https://github.com/greenbtc/greenbtc-blockchain/wiki/Pooling-User-Guide) that allows farmers to have control of making blocks
* Support for light clients with fast, objective syncing
* A growing community of farmers and developers around the world
* Combining Proof-of-Work and Proof-of-Stake Securely

## Installing

Please visit our wiki for more information:
[wiki](https://github.com/greenbtc/greenbtc-blockchain/wiki).

## Resource Links

Staking, You need 10 coin for your 1TB of farming netspace.

GreenBTC Website: https://greenbtc.top

## How to staking

1. Query the stake balance:

   ```
   $ greenbtc stake info
   ...
	Stake Balance: 0.0
	Stake Balance Other: 0.0
	Stake Balance Income: 0.0
	Stake Balance 24H Exp: 0.0
	Stake Reward: 0.0
	Stake Address: dpos:gbtc:1*************************************************
   ...
   ```

2. Send coins to the stake:

   ```
   $ greenbtc stake send -a 1
   ```

3. Withdraw old stake

   ```
   $ greenbtc stake withdraw_old
   ```

   Do a transaction to transfer the coins from the staking address to now wallet receive address.
