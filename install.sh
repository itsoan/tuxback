#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/tuxback"
TARGET_LINK="/usr/local/bin/tuxback"
SOURCE_SCRIPT="$PROJECT_DIR/tuxback"

echo "Installing TuxBack..."

if [[ ! -f "$SOURCE_SCRIPT" ]]; then
    echo "Error: launcher script '$SOURCE_SCRIPT' not found."
    exit 1
fi

chmod +x "$SOURCE_SCRIPT"
chmod +x "$PROJECT_DIR/uninstall.sh" 2>/dev/null || true

echo "Creating installation directory: $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"

echo "Copying project files..."
sudo rsync -a --delete \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude 'backups' \
    --exclude 'restored_data' \
    --exclude 'restored_from_cli' \
    --exclude 'test_data' \
    --exclude 'tuxback.log' \
    --exclude 'schedules.json' \
    "$PROJECT_DIR/" "$INSTALL_DIR/"

sudo chmod +x "$INSTALL_DIR/tuxback"
sudo chmod +x "$INSTALL_DIR/install.sh" "$INSTALL_DIR/uninstall.sh" 2>/dev/null || true

echo "Creating command symlink..."
sudo ln -sf "$INSTALL_DIR/tuxback" "$TARGET_LINK"

echo
echo "TuxBack installed successfully."
echo
echo "Installation directory:"
echo "  $INSTALL_DIR"
echo
echo "Command available globally as:"
echo "  tuxback"
echo
echo "Try running:"
echo "  tuxback --help"
echo "  tuxback --version"
echo "  tuxback status"