from __future__ import annotations

import os
from pathlib import Path

DEFAULT_ROOT_PATH = Path(os.path.expanduser(os.getenv("GREENBTC_ROOT", "~/.greenbtc/mainnet"))).resolve()

DEFAULT_KEYS_ROOT_PATH = Path(os.path.expanduser(os.getenv("GREENBTC_KEYS_ROOT", "~/.greenbtc_keys"))).resolve()

SIMULATOR_ROOT_PATH = Path(os.path.expanduser(os.getenv("GREENBTC_SIMULATOR_ROOT", "~/.greenbtc/simulator"))).resolve()
