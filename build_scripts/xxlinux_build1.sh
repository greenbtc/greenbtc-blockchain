#!/bin/bash

# git clone https://github.com/greenbtc/greenbtc-blockchain.git
# cd greenbtc-blockchain
# git submodule update --init --recursive

echo "clean source ========================="
# git clean -fdx
rm -rf ./build_scripts/build
rm -rf ./build_scripts/dist
cd greenbtc-blockchain-gui
git clean -fdx
cd ../

echo "venv & install ========================="
python3.7 -m venv venv
. ./venv/bin/activate

python -m pip install --upgrade pip
python -m pip install wheel
python -m pip install --extra-index-url https://pypi.chia.net/simple/ miniupnpc==2.1
python -m pip install -e . --extra-index-url https://pypi.chia.net/simple/

python -m pip install setuptools_scm
python -m pip install pyinstaller==4.2


echo "cd build_scripts & pyinstaller ========================="
cd build_scripts
mkdir dist


SPEC_FILE=$(python -c 'import greenbtc; print(greenbtc.PYINSTALLER_SPEC_PATH)')
# SPEC_FILE='../greenbtc/pyinstaller.spec'
pyinstaller --log-level=INFO "$SPEC_FILE"
LAST_EXIT_CODE=$?
if [ "$LAST_EXIT_CODE" -ne 0 ]; then
	echo >&2 "pyinstaller failed!"
	exit $LAST_EXIT_CODE
fi

deactivate

echo "cp daemon ========================="
#daemon
#cp -r dist/daemon ../greenbtc-blockchain-gui
rm -rf ../../greenbtc-linux
cp -r dist/daemon ../../greenbtc-linux
cd ../

