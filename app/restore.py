import logging
import tarfile
from pathlib import Path
from app.storage import backup_exists, get_backup_path

logger = logging.getLogger(__name__)

def _is_within_directory(base: Path, target: Path) -> bool:
    "Проверяет, что путь target находится внутри base."
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def restore_backup(filename: str, target_path: str) -> Path:
    "Восстанавливает архив резервной копии в указанную директорию."
    logger.info("Starting restore: filename=%s target=%s", filename, target_path)

    if not backup_exists(filename):
        logger.error("Backup file not found: %s", filename)
        raise FileNotFoundError(f"Backup file not found: {filename}")

    archive_path = get_backup_path(filename)
    target = Path(target_path).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    logger.debug("Restore archive path: %s", archive_path)
    logger.debug("Restore target path: %s", target)

    with tarfile.open(archive_path, "r:gz") as tar:
        members = tar.getmembers()
        logger.debug("Archive contains %d member(s)", len(members))

        for member in members:
            destination = target / member.name
            if not _is_within_directory(target, destination):
                logger.error("Unsafe archive member detected: %s", member.name)
                raise ValueError(f"Unsafe archive member detected: {member.name}")

        tar.extractall(path=target, members=members)

    logger.info(
        "Backup restored successfully: filename=%s target=%s extracted_members=%d",
        filename,
        target,
        len(members),
    )
    return target