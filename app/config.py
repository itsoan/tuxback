import logging
import os
from pathlib import Path

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Метаданные приложения
APP_NAME = "TuxBack"
APP_VERSION = "1.0.0"
APP_DIR_NAME = "tuxback"
TIME_FORMAT = "%Y%m%d_%H%M%S"

# XDG-совместимые директории пользователя.
# Это позволяет приложению работать без sudo после установки.
HOME_DIR = Path.home()
XDG_DATA_HOME = Path(os.environ.get("XDG_DATA_HOME", HOME_DIR / ".local" / "share"))
XDG_STATE_HOME = Path(os.environ.get("XDG_STATE_HOME", HOME_DIR / ".local" / "state"))
XDG_CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", HOME_DIR / ".config"))

# Пользователь может переопределить пути через переменные окружения.
DATA_DIR = Path(os.environ.get("TUXBACK_DATA_DIR", XDG_DATA_HOME / APP_DIR_NAME))
STATE_DIR = Path(os.environ.get("TUXBACK_STATE_DIR", XDG_STATE_HOME / APP_DIR_NAME))
CONFIG_DIR = Path(os.environ.get("TUXBACK_CONFIG_DIR", XDG_CONFIG_HOME / APP_DIR_NAME))

# Рабочие директории и файлы приложения
BACKUP_DIR = DATA_DIR / "backups"
SCHEDULE_FILE = CONFIG_DIR / "schedules.json"
LOG_FILE = STATE_DIR / "tuxback.log"


def ensure_directories() -> None:
    "Создаёт все необходимые директории приложения."
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging() -> None:
    "Настраивает логирование в консоль и в файл."
    ensure_directories()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(levelname)s | %(message)s")
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
        )
    )

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler],
        force=True,
    )

    logger = logging.getLogger(__name__)
    logger.debug("Logging configured")
    logger.debug("BASE_DIR=%s", BASE_DIR)
    logger.debug("DATA_DIR=%s", DATA_DIR)
    logger.debug("STATE_DIR=%s", STATE_DIR)
    logger.debug("CONFIG_DIR=%s", CONFIG_DIR)
    logger.debug("BACKUP_DIR=%s", BACKUP_DIR)
    logger.debug("SCHEDULE_FILE=%s", SCHEDULE_FILE)
    logger.debug("LOG_FILE=%s", LOG_FILE)