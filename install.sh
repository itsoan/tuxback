#!/usr/bin/env bash

# Включаем строгий режим выполнения скрипта:
# -e  : завершать скрипт при любой ошибке
# -u  : ошибка при использовании неинициализированной переменной
# -o pipefail : если любая команда в pipe завершится с ошибкой — весь pipe считается ошибкой
set -euo pipefail

# Определяем директорию, в которой находится текущий скрипт install.sh
# dirname — получает директорию файла
# cd + pwd — преобразует путь в абсолютный
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Директория, куда будет установлен проект
INSTALL_DIR="/opt/tuxback"

# Глобальная команда, через которую пользователь будет запускать утилиту
TARGET_LINK="/usr/local/bin/tuxback"

# Путь к исполняемому launcher‑скрипту tuxback
SOURCE_SCRIPT="$PROJECT_DIR/tuxback"

# Имена systemd сервисов
SERVICE_NAME="tuxback-scheduler.service"
TIMER_NAME="tuxback-scheduler.timer"

# Полные пути systemd unit файлов
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
TIMER_PATH="/etc/systemd/system/$TIMER_NAME"

# Сообщение о начале установки
echo "Installing TuxBack..."

# Проверяем, существует ли launcher tuxback
if [[ ! -f "$SOURCE_SCRIPT" ]]; then
    echo "Error: launcher script '$SOURCE_SCRIPT' not found."
    exit 1
fi

# Делаем launcher исполняемым
chmod +x "$SOURCE_SCRIPT"

# Делаем uninstall.sh исполняемым (если он существует)
chmod +x "$PROJECT_DIR/uninstall.sh" 2>/dev/null || true

# Создаём директорию установки
# sudo требуется потому что /opt — системная директория
echo "Creating installation directory: $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"

# Копируем файлы проекта в /opt/tuxback
# rsync используется для корректного и быстрого копирования
# --delete удаляет старые файлы при переустановке
# --exclude исключает ненужные файлы
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

# Делаем установленные скрипты исполняемыми
sudo chmod +x "$INSTALL_DIR/tuxback"
sudo chmod +x "$INSTALL_DIR/install.sh" "$INSTALL_DIR/uninstall.sh" 2>/dev/null || true

# Создаём симлинк глобальной команды tuxback
# После этого пользователь сможет запускать программу из любой директории
echo "Creating command symlink..."
sudo ln -sf "$INSTALL_DIR/tuxback" "$TARGET_LINK"

# Создаём systemd service
# Этот сервис будет запускать планировщик резервных копий
echo "Installing systemd service..."
sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=TuxBack scheduled backup runner
After=network.target

[Service]
Type=oneshot
WorkingDirectory=$INSTALL_DIR
ExecStart=$TARGET_LINK run-scheduler
EOF

# Создаём systemd timer
# Таймер будет запускать сервис по расписанию
echo "Installing systemd timer..."
sudo tee "$TIMER_PATH" > /dev/null <<EOF
[Unit]
Description=Run TuxBack scheduler every minute

[Timer]
# Выполнять каждую минуту
OnCalendar=*-*-* *:*:00

# Если система была выключена — выполнить пропущенную задачу
Persistent=true

Unit=$SERVICE_NAME

[Install]
WantedBy=timers.target
EOF

# Перезагружаем systemd конфигурацию
# и сразу включаем таймер
echo "Enabling systemd timer..."
sudo systemctl daemon-reload
sudo systemctl enable --now "$TIMER_NAME"

# Финальная информация для пользователя
echo
echo "TuxBack installed successfully."
echo
echo "Installation directory:"
echo "  $INSTALL_DIR"
echo
echo "Command available globally as:"
echo "  tuxback"
echo
echo "Systemd timer enabled as:"
echo "  $TIMER_NAME"
echo
echo "Try running:"
echo "  tuxback --help"
echo "  tuxback --version"
echo "  tuxback status"
echo "  systemctl status $TIMER_NAME"
echo "  journalctl -u $SERVICE_NAME -n 20 --no-pager"