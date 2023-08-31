#!/usr/bin/env bash
# Post install script for the UI .rpm to place symlinks in places to allow the CLI to work similarly in both versions

set -e

ln -s /opt/greenbtc/resources/app.asar.unpacked/daemon/greenbtc /usr/bin/greenbtc || true
ln -s /opt/greenbtc/greenbtc-blockchain /usr/bin/greenbtc-blockchain || true
