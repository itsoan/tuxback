#!/usr/bin/env bash

set -euo pipefail

INSTALL_DIR="/opt/tuxback"
TARGET_LINK="/usr/local/bin/tuxback"
SERVICE_NAME="tuxback-scheduler.service"
TIMER_NAME="tuxback-scheduler.timer"
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
SERVICE_PATH="$USER_SYSTEMD_DIR/$SERVICE_NAME"
TIMER_PATH="$USER_SYSTEMD_DIR/$TIMER_NAME"

echo "Removing TuxBack..."

echo "Stopping and disabling user-level systemd timer..."
systemctl --user disable --now "$TIMER_NAME" 2>/dev/null || true

echo "Removing user-level systemd unit files..."
rm -f "$SERVICE_PATH" "$TIMER_PATH"
systemctl --user daemon-reload 2>/dev/null || true

if [[ -L "$TARGET_LINK" || -f "$TARGET_LINK" ]]; then
    sudo rm -f "$TARGET_LINK"
    echo "Removed symlink:"
    echo "  $TARGET_LINK"
else
    echo "Symlink not found:"
    echo "  $TARGET_LINK"
fi

if [[ -d "$INSTALL_DIR" ]]; then
    sudo rm -rf "$INSTALL_DIR"
    echo "Removed installation directory:"
    echo "  $INSTALL_DIR"
else
    echo "Installation directory not found:"
    echo "  $INSTALL_DIR"
fi

echo
echo "TuxBack removed successfully."
echo "Run 'hash -r' or open a new shell if your shell still remembers the old command path."

hash -r 2>/dev/null || true