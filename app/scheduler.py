import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from app.backup import create_backup
from app.config import SCHEDULE_FILE

logger = logging.getLogger(__name__)


# Loads all scheduled backup tasks from the JSON file.
def load_schedules() -> List[Dict[str, Any]]:
    if not SCHEDULE_FILE.exists():
        logger.info("Schedule file does not exist yet: %s", SCHEDULE_FILE)
        return []

    with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
        schedules = json.load(file)

    logger.info("Loaded %d scheduled task(s)", len(schedules))
    return schedules


# Saves the current list of scheduled tasks to the JSON file.
def save_schedules(schedules: List[Dict[str, Any]]) -> None:
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as file:
        json.dump(schedules, file, indent=4, ensure_ascii=False)

    logger.info("Saved %d scheduled task(s)", len(schedules))


# Adds a new scheduled backup task.
# The function validates both the source directory and the interval.
def add_schedule(source: str, interval_minutes: int) -> Dict[str, Any]:
    source_path = Path(source)

    if not source_path.exists():
        logger.error("Schedule source path does not exist: %s", source)
        raise FileNotFoundError(f"Source path does not exist: {source}")

    if not source_path.is_dir():
        logger.error("Schedule source path is not a directory: %s", source)
        raise ValueError("Schedule source must be a directory")

    if interval_minutes <= 0:
        logger.error("Invalid schedule interval: %s", interval_minutes)
        raise ValueError("Interval must be greater than 0 minutes")

    schedules = load_schedules()

    new_schedule = {
        "id": len(schedules) + 1,
        "source": source,
        "interval_minutes": interval_minutes,
        "enabled": True,
        "last_run": None,
    }

    schedules.append(new_schedule)
    save_schedules(schedules)
    logger.info("Added new schedule: %s", new_schedule)
    return new_schedule


# Returns the full list of configured scheduled tasks.
def list_schedules() -> List[Dict[str, Any]]:
    return load_schedules()


# Deletes a scheduled task by its numeric identifier.
def delete_schedule(schedule_id: int) -> bool:
    schedules = load_schedules()
    updated_schedules = [
        schedule for schedule in schedules
        if schedule["id"] != schedule_id
    ]

    if len(updated_schedules) == len(schedules):
        logger.warning("Schedule not found for deletion: %s", schedule_id)
        return False

    save_schedules(updated_schedules)
    logger.info("Deleted schedule with ID: %s", schedule_id)
    return True


# Runs all enabled scheduled tasks that are due.
def run_due_schedules() -> List[Dict[str, Any]]:
    schedules = load_schedules()
    results: List[Dict[str, Any]] = []
    now = datetime.now()
    updated = False

    for schedule in schedules:
        if not schedule.get("enabled", True):
            logger.info("Skipping disabled schedule ID: %s", schedule["id"])
            continue

        last_run_raw = schedule.get("last_run")
        interval_minutes = schedule["interval_minutes"]
        should_run = False

        if last_run_raw is None:
            should_run = True
        else:
            last_run = datetime.fromisoformat(last_run_raw)
            next_run = last_run + timedelta(minutes=interval_minutes)
            should_run = now >= next_run

        if not should_run:
            logger.info("Schedule is not due yet, ID: %s", schedule["id"])
            continue

        archive_name = create_backup(schedule["source"])
        schedule["last_run"] = now.isoformat(timespec="seconds")
        updated = True

        result = {
            "id": schedule["id"],
            "source": schedule["source"],
            "archive": archive_name,
            "run_at": schedule["last_run"],
        }
        results.append(result)
        logger.info("Executed scheduled backup: %s", result)

    if updated:
        save_schedules(schedules)

    return results