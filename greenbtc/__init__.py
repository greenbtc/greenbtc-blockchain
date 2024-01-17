from __future__ import annotations

import importlib.metadata

__version__: str
try:
    __version__ = importlib.metadata.version("greenbtc-blockchain")
except importlib.metadata.PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"
