import nest_asyncio
from pkg_resources import DistributionNotFound, get_distribution, resource_filename

nest_asyncio.apply()

try:
    __version__ = "1.6.0"
except DistributionNotFound:
    # package is not installed
    __version__ = "unknown"

PYINSTALLER_SPEC_PATH = resource_filename("greenbtc", "pyinstaller.spec")
