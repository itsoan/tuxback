import logging
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Tuple

from app.config import TIME_FORMAT
from app.storage import get_backup_path, init_storage

logger = logging.getLogger(__name__)


def _collect_source_stats(source: Path) -> Tuple[int, int, int]:
    "Подсчитывает количество файлов, директорий и общий размер источника."
    file_count = 0
    dir_count = 0
    total_bytes = 0

    for path in source.rglob("*"):
        if path.is_dir():
            dir_count += 1
        elif path.is_file():
            file_count += 1
            try:
                total_bytes += path.stat().st_size
            except OSError:
                logger.debug("Could not read file size: %s", path, exc_info=True)

    return file_count, dir_count, total_bytes


def create_backup(source_path: str) -> str:
    "Создаёт архив резервной копии для указанной директории."
    init_storage()

    source = Path(source_path).expanduser().resolve()
    logger.info("Starting backup: source=%s", source)

    if not source.exists():
        logger.error("Backup source path does not exist: %s", source)
        raise FileNotFoundError(f"Source path does not exist: {source}")

    if not source.is_dir():
        logger.error("Backup source is not a directory: %s", source)
        raise ValueError("Backup source must be a directory")

    file_count, dir_count, total_bytes = _collect_source_stats(source)
    logger.debug(
        "Backup source stats: files=%d dirs=%d size_bytes=%d",
        file_count,
        dir_count,
        total_bytes,
    )

    timestamp = datetime.now().strftime(TIME_FORMAT)
    archive_name = f"{source.name}_{timestamp}.tar.gz"
    archive_path = get_backup_path(archive_name)

    logger.debug("Archive name generated: %s", archive_name)
    logger.debug("Archive path resolved: %s", archive_path)

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(source, arcname=source.name)

    archive_size = archive_path.stat().st_size if archive_path.exists() else 0
    logger.info(
        "Backup created successfully: archive=%s size_bytes=%d source_files=%d source_dirs=%d",
        archive_path,
        archive_size,
        file_count,
        dir_count,
    )
    return archive_name