import logging
from pathlib import Path
from typing import List

from app.config import (
    BACKUP_DIR,
    CONFIG_DIR,
    LOG_FILE,
    SCHEDULE_FILE,
    STATE_DIR,
    ensure_directories,
)

logger = logging.getLogger(__name__)


def init_storage() -> None:
    "Инициализирует рабочие директории приложения."
    ensure_directories()
    logger.debug("Storage initialized")
    logger.debug("BACKUP_DIR=%s", BACKUP_DIR)
    logger.debug("CONFIG_DIR=%s", CONFIG_DIR)
    logger.debug("STATE_DIR=%s", STATE_DIR)
    logger.debug("SCHEDULE_FILE=%s", SCHEDULE_FILE)
    logger.debug("LOG_FILE=%s", LOG_FILE)


def get_backup_path(filename: str) -> Path:
    "Возвращает полный путь к архиву резервной копии."
    path = BACKUP_DIR / filename
    logger.debug("Resolved backup path for %s -> %s", filename, path)
    return path


def backup_exists(filename: str) -> bool:
    "Проверяет существование архива."
    exists = get_backup_path(filename).exists()
    logger.info("Backup exists check: filename=%s exists=%s", filename, exists)
    return exists


def list_backups() -> List[str]:
    "Возвращает отсортированный список всех архивов .tar.gz."
    init_storage()

    backups = [
        file.name
        for file in BACKUP_DIR.iterdir()
        if file.is_file() and file.suffixes[-2:] == [".tar", ".gz"]
    ]

    sorted_backups = sorted(backups)
    logger.info("Listed %d backup file(s)", len(sorted_backups))
    logger.debug("Backup files: %s", sorted_backups)
    return sorted_backups


def delete_backup(filename: str) -> bool:
    "Удаляет архив резервной копии по имени."
    backup_file = get_backup_path(filename)

    if backup_file.exists() and backup_file.is_file():
        file_size = backup_file.stat().st_size
        backup_file.unlink()
        logger.info(
            "Backup deleted successfully: filename=%s size_bytes=%d",
            filename,
            file_size,
        )
        return True

    logger.warning("Backup file not found for deletion: %s", filename)
    return False