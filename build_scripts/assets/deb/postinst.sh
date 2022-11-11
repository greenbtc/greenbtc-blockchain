#!/usr/bin/env bash
# Post install script for the UI .deb to place symlinks in places to allow the CLI to work similarly in both versions

set -e

ln -s /opt/greenbtc/resources/app.asar.unpacked/daemon/greenbtc /usr/bin/greenbtc || true
