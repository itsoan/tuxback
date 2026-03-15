import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / "backups"
SCHEDULE_FILE = BASE_DIR / "schedules.json"
LOG_FILE = BASE_DIR / "tuxback.log"
TIME_FORMAT = "%Y%m%d_%H%M%S"
APP_NAME = "TuxBack"
APP_VERSION = "1.0.0"


# Creates required directories for the application.
def ensure_directories() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# Configures logging for console output and file output.
def setup_logging() -> None:
    ensure_directories()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )