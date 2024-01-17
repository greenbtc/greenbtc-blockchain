from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from greenbtc.types.blockchain_format.coin import Coin
from greenbtc.types.blockchain_format.sized_bytes import bytes32
from greenbtc.types.coin_record import CoinRecord
from greenbtc.util.ints import uint8, uint32, uint64
from greenbtc.util.misc import VersionedBlob
from greenbtc.wallet.puzzles.clawback.metadata import ClawbackMetadata, ClawbackVersion
from greenbtc.wallet.puzzles.stake.metadata import StakeMetadata, StakeVersion
from greenbtc.wallet.util.wallet_types import CoinType, StreamableWalletIdentifier, WalletType
from greenbtc.wallet.vc_wallet.cr_cat_drivers import CRCATMetadata, CRCATVersion

MetadataTypes = Union[ClawbackMetadata, CRCATMetadata, StakeMetadata]


@dataclass(frozen=True)
class WalletCoinRecord:
    """
    These are values that correspond to a CoinName that are used
    in keeping track of the unspent database.
    """

    coin: Coin
    confirmed_block_height: uint32
    spent_block_height: uint32
    spent: bool
    coinbase: bool
    wallet_type: WalletType
    wallet_id: int
    # Cannot include new attributes in the hash since they will change the coin order in a set.
    # The launcher coin ID will change and will break all hardcode offer tests in CAT/NFT/DL, etc.
    # TODO Change hardcode offer in unit tests
    coin_type: CoinType = field(default=CoinType.NORMAL, hash=False)
    metadata: Optional[VersionedBlob] = field(default=None, hash=False)

    def wallet_identifier(self) -> StreamableWalletIdentifier:
        return StreamableWalletIdentifier(uint32(self.wallet_id), uint8(self.wallet_type))

    def parsed_metadata(self) -> MetadataTypes:
        if self.metadata is None:
            raise ValueError("Can't parse None metadata")
        if self.coin_type == CoinType.STAKE and self.metadata.version == StakeVersion.V1.value:
            return StakeMetadata.from_bytes(self.metadata.blob)
        if self.coin_type == CoinType.CLAWBACK and self.metadata.version == ClawbackVersion.V1.value:
            return ClawbackMetadata.from_bytes(self.metadata.blob)
        if (
            self.coin_type in {CoinType.CRCAT_PENDING, CoinType.CRCAT}
            and self.metadata.version == CRCATVersion.V1.value
        ):
            return CRCATMetadata.from_bytes(self.metadata.blob)
        raise ValueError(f"Unknown metadata {self.metadata} for coin_type {self.coin_type}")

    def name(self) -> bytes32:
        return self.coin.name()

    def to_coin_record(self, timestamp: uint64) -> CoinRecord:
        return CoinRecord(self.coin, self.confirmed_block_height, self.spent_block_height, self.coinbase, timestamp)

    def to_json_dict_parsed_metadata(self) -> Dict[str, Any]:
        # TODO: Merge wallet_type and wallet_id into `wallet_identifier`, make `spent` an attribute based
        #  on `spent_height` make `WalletCoinRecord` streamable and use Streamable.to_json_dict as base here if we have
        #  streamable enums.
        json_dict = None
        if self.metadata is not None:
            if self.coin_type == CoinType.STAKE:
                metadata = self.parsed_metadata()
                json_dict = metadata.to_json_dict()
                json_dict["time_lock"] = metadata.time_lock
            else:
                json_dict = self.parsed_metadata().to_json_dict()
        return {
            **self.coin.to_json_dict(),
            "id": "0x" + self.name().hex(),
            "type": int(self.coin_type),
            "wallet_identifier": self.wallet_identifier().to_json_dict(),
            "metadata": json_dict,
            "confirmed_height": self.confirmed_block_height,
            "spent_height": self.spent_block_height,
            "coinbase": self.coinbase,
        }
