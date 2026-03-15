#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_LINK="/usr/local/bin/tuxback"
SOURCE_SCRIPT="$PROJECT_DIR/tuxback"

echo "Installing TuxBack..."

if [[ ! -f "$SOURCE_SCRIPT" ]]; then
    echo "Error: launcher script '$SOURCE_SCRIPT' not found."
    exit 1
fi

chmod +x "$SOURCE_SCRIPT"

sudo ln -sf "$SOURCE_SCRIPT" "$TARGET_LINK"

echo "TuxBack installed successfully."
echo "Command available as: tuxback"
echo
echo "Examples:"
echo "  tuxback --help"
echo "  tuxback --version"
echo "  tuxback status"