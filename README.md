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

Staking, You need 2 coin for your 1TB of farming netspace.

GreenBTC Website: https://greenbtc.top

## How to staking

1. Query the staking balance:

   ```
   $ greenbtc wallet staking_info
   ...
   Staking balance:  0
   Staking address:  gbtc16h0zj4q0uyt3frl7tmcy9whl30xv75g7qqcgulwht79a04ahxyrsmf56se
   ...
   ```

2. Send coins to the staking:

   ```
   $ greenbtc wallet staking -a 1
   ```

   Wait for the transaction get confirmed, query staking balance again:

   ```
   $ greenbtc wallet staking_info
   ...
   Staking balance:  1
   Staking address:  gbtc16h0zj4q0uyt3frl7tmcy9whl30xv75g7qqcgulwht79a04ahxyrsmf56se
   ...
   ```

3. Withdraw coins from the staking address:

   ```
   $ greenbtc wallet staking_withdraw -a 1
   ```

   Do a transaction to transfer the coins from the staking address to now wallet receive address.

   Make sure to choose the wallet that contains the plot farmer key.
