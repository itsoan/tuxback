#!/usr/bin/env bash

# Включаем строгий режим выполнения скрипта:
# -e  : завершать скрипт при любой ошибке
# -u  : ошибка при использовании неинициализированной переменной
# -o pipefail : если любая команда в pipe завершится с ошибкой — весь pipe считается ошибкой
set -euo pipefail

# Директория, в которой установлен проект
INSTALL_DIR="/opt/tuxback"

# Глобальная команда tuxback (символическая ссылка)
TARGET_LINK="/usr/local/bin/tuxback"

# Имена systemd сервисов, созданных во время установки
SERVICE_NAME="tuxback-scheduler.service"
TIMER_NAME="tuxback-scheduler.timer"

# Полные пути к systemd unit-файлам
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
TIMER_PATH="/etc/systemd/system/$TIMER_NAME"

# Сообщение о начале удаления
echo "Removing TuxBack..."

# Останавливаем и отключаем systemd таймер
# 2>/dev/null || true используется, чтобы не прерывать скрипт,
# если таймер уже не существует
echo "Stopping and disabling systemd timer..."
sudo systemctl disable --now "$TIMER_NAME" 2>/dev/null || true

# Удаляем systemd unit-файлы сервиса и таймера
# После удаления необходимо перезагрузить конфигурацию systemd
echo "Removing systemd unit files..."
sudo rm -f "$SERVICE_PATH" "$TIMER_PATH"

# Перезагружаем конфигурацию systemd
sudo systemctl daemon-reload

# Сбрасываем статус failed сервисов (если он был)
sudo systemctl reset-failed 2>/dev/null || true


# Удаляем глобальную команду tuxback
# Проверяем, существует ли симлинк или файл
if [[ -L "$TARGET_LINK" || -f "$TARGET_LINK" ]]; then
    sudo rm -f "$TARGET_LINK"
    echo "Removed symlink:"
    echo "  $TARGET_LINK"
else
    echo "Symlink not found:"
    echo "  $TARGET_LINK"
fi

# Удаляем директорию установки /opt/tuxback
# В ней находятся все файлы проекта
if [[ -d "$INSTALL_DIR" ]]; then
    sudo rm -rf "$INSTALL_DIR"
    echo "Removed installation directory:"
    echo "  $INSTALL_DIR"
else
    echo "Installation directory not found:"
    echo "  $INSTALL_DIR"
fi

# Финальное сообщение пользователю
echo
echo "TuxBack removed successfully."
echo "Run 'hash -r' or open a new shell if your shell still remembers the old command path."


# Очищаем кэш команд bash
# Это нужно чтобы shell "забыл" старый путь к tuxback
hash -r 2>/dev/null || true