# -*- mode: python ; coding: utf-8 -*-
import importlib
import os
import pathlib
import platform
import sysconfig

from pkg_resources import get_distribution

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

THIS_IS_WINDOWS = platform.system().lower().startswith("win")
THIS_IS_MAC = platform.system().lower().startswith("darwin")

ROOT = pathlib.Path(importlib.import_module("greenbtc").__file__).absolute().parent.parent


def solve_name_collision_problem(analysis):
    """
    There is a collision between the `greenbtc` file name (which is the executable)
    and the `greenbtc` directory, which contains non-code resources like `english.txt`.
    We move all the resources in the zipped area so there is no
    need to create the `greenbtc` directory, since the names collide.

    Fetching data now requires going into a zip file, so it will be slower.
    It's best if files that are used frequently are cached.

    A sample large compressible file (1 MB of `/dev/zero`), seems to be
    about eight times slower.

    Note that this hack isn't documented, but seems to work.
    """

    zipped = []
    datas = []
    for data in analysis.datas:
        if str(data[0]).startswith("greenbtc/"):
            zipped.append(data)
        else:
            datas.append(data)

    # items in this field are included in the binary
    analysis.zipped_data = zipped

    # these items will be dropped in the root folder uncompressed
    analysis.datas = datas


keyring_imports = collect_submodules("keyring.backends")

# keyring uses entrypoints to read keyring.backends from metadata file entry_points.txt.
keyring_datas = copy_metadata("keyring")[0]

version_data = copy_metadata(get_distribution("greenbtc-blockchain"))[0]

block_cipher = None

SERVERS = [
    "data_layer",
    "wallet",
    "full_node",
    "harvester",
    "farmer",
    "introducer",
    "timelord",
]

if THIS_IS_WINDOWS:
    hidden_imports_for_windows = ["win32timezone", "win32cred", "pywintypes", "win32ctypes.pywin32"]
else:
    hidden_imports_for_windows = []

hiddenimports = [
    *collect_submodules("greenbtc"),
    *keyring_imports,
    *hidden_imports_for_windows,
]

binaries = []

if THIS_IS_WINDOWS:
    greenbtc_mod = importlib.import_module("greenbtc")
    dll_paths = pathlib.Path(sysconfig.get_path("platlib")) / "*.dll"

    binaries = [
        (
            dll_paths,
            ".",
        ),
        (
            "C:\\Windows\\System32\\msvcp140.dll",
            ".",
        ),
        (
            "C:\\Windows\\System32\\vcruntime140_1.dll",
            ".",
        ),
    ]
    if os.path.exists(f"{ROOT}/madmax/chia_plot.exe"):
        binaries.extend([
            (
                f"{ROOT}/madmax/chia_plot.exe",
                "madmax"
            )
        ])

    if os.path.exists(f"{ROOT}/madmax/chia_plot_k34.exe",):
        binaries.extend([
            (
                f"{ROOT}/madmax/chia_plot_k34.exe",
                "madmax"
            )
        ])

    if os.path.exists(f"{ROOT}/bladebit/bladebit.exe"):
        binaries.extend([
            (
                f"{ROOT}/bladebit/bladebit.exe",
                "bladebit"
            )
        ])

    if os.path.exists(f"{ROOT}/bladebit/bladebit_cuda.exe"):
        binaries.extend([
            (
                f"{ROOT}/bladebit/bladebit_cuda.exe",
                "bladebit"
            )
        ])
else:
    if os.path.exists(f"{ROOT}/madmax/chia_plot"):
        binaries.extend([
            (
                f"{ROOT}/madmax/chia_plot",
                "madmax"
            )
        ])

    if os.path.exists(f"{ROOT}/madmax/chia_plot_k34",):
        binaries.extend([
            (
                f"{ROOT}/madmax/chia_plot_k34",
                "madmax"
            )
        ])

    if os.path.exists(f"{ROOT}/bladebit/bladebit"):
        binaries.extend([
            (
                f"{ROOT}/bladebit/bladebit",
                "bladebit"
            )
        ])

    if os.path.exists(f"{ROOT}/bladebit/bladebit_cuda"):
        binaries.extend([
            (
                f"{ROOT}/bladebit/bladebit_cuda",
                "bladebit"
            )
        ])

datas = []

datas.append((f"{ROOT}/greenbtc/util/english.txt", "greenbtc/util"))
datas.append((f"{ROOT}/greenbtc/util/initial-config.yaml", "greenbtc/util"))
for path in sorted({path.parent for path in ROOT.joinpath("greenbtc").rglob("*.hex")}):
    datas.append((f"{path}/*.hex", path.relative_to(ROOT)))
datas.append((f"{ROOT}/greenbtc/ssl/*", "greenbtc/ssl"))
datas.append((f"{ROOT}/mozilla-ca/*", "mozilla-ca"))
datas.append(version_data)

pathex = []


def add_binary(name, path_to_script, collect_args):
    analysis = Analysis(
        [path_to_script],
        pathex=pathex,
        binaries=binaries,
        datas=datas,
        hiddenimports=hiddenimports,
        hookspath=[],
        runtime_hooks=[],
        excludes=[],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False,
    )

    solve_name_collision_problem(analysis)

    binary_pyz = PYZ(analysis.pure, analysis.zipped_data, cipher=block_cipher)

    binary_exe = EXE(
        binary_pyz,
        analysis.scripts,
        [],
        exclude_binaries=True,
        name=name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
    )

    collect_args.extend(
        [
            binary_exe,
            analysis.binaries,
            analysis.zipfiles,
            analysis.datas,
        ]
    )


COLLECT_ARGS = []

add_binary("greenbtc", f"{ROOT}/greenbtc/cmds/greenbtc.py", COLLECT_ARGS)
add_binary("greenbtc_daemon", f"{ROOT}/greenbtc/daemon/server.py", COLLECT_ARGS)

for server in SERVERS:
    add_binary(f"greenbtc_{server}", f"{ROOT}/greenbtc/server/start_{server}.py", COLLECT_ARGS)

add_binary("greenbtc_crawler", f"{ROOT}/greenbtc/seeder/start_crawler.py", COLLECT_ARGS)
add_binary("greenbtc_seeder", f"{ROOT}/greenbtc/seeder/dns_server.py", COLLECT_ARGS)
add_binary("greenbtc_data_layer_http", f"{ROOT}/greenbtc/data_layer/data_layer_server.py", COLLECT_ARGS)
add_binary("greenbtc_data_layer_s3_plugin", f"{ROOT}/greenbtc/data_layer/s3_plugin_service.py", COLLECT_ARGS)
add_binary("greenbtc_timelord_launcher", f"{ROOT}/greenbtc/timelord/timelord_launcher.py", COLLECT_ARGS)

COLLECT_KWARGS = dict(
    strip=False,
    upx_exclude=[],
    name="daemon",
)

coll = COLLECT(*COLLECT_ARGS, **COLLECT_KWARGS)
