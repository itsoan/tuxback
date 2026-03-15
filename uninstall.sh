#!/usr/bin/env bash

set -euo pipefail

TARGET_LINK="/usr/local/bin/tuxback"

echo "Removing TuxBack..."

if [[ -L "$TARGET_LINK" || -f "$TARGET_LINK" ]]; then
    sudo rm -f "$TARGET_LINK"
    echo "TuxBack removed successfully."
else
    echo "TuxBack is not installed."
fi