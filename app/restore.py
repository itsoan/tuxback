import logging
import tarfile
from pathlib import Path

from app.storage import backup_exists, get_backup_path

logger = logging.getLogger(__name__)


# Verifies that every extracted file will stay inside the target directory.
def _is_within_directory(base: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


# Restores a backup archive into the specified target directory.
# Before extraction, all archive members are validated to prevent
# path traversal outside the destination directory.
def restore_backup(filename: str, target_path: str) -> Path:
    logger.info("Starting restore for archive: %s", filename)

    if not backup_exists(filename):
        logger.error("Backup file not found: %s", filename)
        raise FileNotFoundError(f"Backup file not found: {filename}")

    archive_path = get_backup_path(filename)
    target = Path(target_path)
    target.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive_path, "r:gz") as tar:
        members = tar.getmembers()

        for member in members:
            destination = target / member.name
            if not _is_within_directory(target, destination):
                logger.error("Unsafe archive member detected: %s", member.name)
                raise ValueError(f"Unsafe archive member detected: {member.name}")

        tar.extractall(path=target, members=members)

    logger.info("Backup restored successfully to: %s", target)
    return target