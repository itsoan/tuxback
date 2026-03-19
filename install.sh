##!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/tuxback"
TARGET_LINK="/usr/local/bin/tuxback"
SOURCE_SCRIPT="$PROJECT_DIR/tuxback"
SERVICE_NAME="tuxback-scheduler.service"
TIMER_NAME="tuxback-scheduler.timer"
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
SERVICE_PATH="$USER_SYSTEMD_DIR/$SERVICE_NAME"
TIMER_PATH="$USER_SYSTEMD_DIR/$TIMER_NAME"

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

sudo ln -sf "$INSTALL_DIR/tuxback" "$TARGET_LINK"

mkdir -p "$USER_SYSTEMD_DIR"

echo "Installing user-level systemd service..."
cat > "$SERVICE_PATH" <<EOF
[Unit]
Description=TuxBack scheduled backup runner
After=default.target

[Service]
Type=oneshot
WorkingDirectory=$INSTALL_DIR
ExecStart=$TARGET_LINK run-scheduler
EOF

echo "Installing user-level systemd timer..."
cat > "$TIMER_PATH" <<EOF
[Unit]
Description=Run TuxBack scheduler every minute

[Timer]
OnCalendar=*-*-* *:*:00
Persistent=true
Unit=$SERVICE_NAME

[Install]
WantedBy=timers.target
EOF

sudo loginctl enable-linger "$USER" 2>/dev/null || true

systemctl --user daemon-reload
systemctl --user enable --now "$TIMER_NAME"

echo
echo "TuxBack installed successfully."
echo
echo "Program files installed to:"
echo "  $INSTALL_DIR"
echo
echo "Global command available as:"
echo "  tuxback"
echo
echo "User data, schedules and logs are now stored in your home directory."
echo "This means TuxBack can be used without sudo after installation."
echo
echo "User systemd timer enabled as:"
echo "  $TIMER_NAME"
echo
echo "Try running:"
echo "  tuxback --help"
echo "  tuxback --version"
echo "  tuxback status"
echo "  systemctl --user status $TIMER_NAME"
echo "  journalctl --user -u $SERVICE_NAME -n 20 --no-pager"