#!/usr/bin/env bash
# Pre remove script for the UI .deb to clean up the symlinks from the installer

set -e

unlink /usr/bin/greenbtc || true
unlink /usr/bin/greenbtc-blockchain || true
