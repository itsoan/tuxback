import json
from datetime import datetime, timedelta
from typing import Any, Dict, List
from app.backup import create_backup
from app.config import SCHEDULE_FILE


# Loads all scheduled backup tasks from the JSON file.
# If the file does not exist yet, an empty list is returned.
def load_schedules() -> List[Dict[str, Any]]:
    if not SCHEDULE_FILE.exists():
        return []

    with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# Saves the current list of scheduled tasks to the JSON file.
def save_schedules(schedules: List[Dict[str, Any]]) -> None:
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as file:
        json.dump(schedules, file, indent=4, ensure_ascii=False)


# Adds a new scheduled backup task.
# Each task stores the source directory, execution interval,
# whether the task is enabled, and the time of the last run.
def add_schedule(source: str, interval_minutes: int) -> Dict[str, Any]:
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

    return new_schedule


# Returns the full list of configured scheduled tasks.
def list_schedules() -> List[Dict[str, Any]]:
    return load_schedules()


# Deletes a scheduled task by its numeric identifier.
# Returns True if the task was removed, otherwise False.
def delete_schedule(schedule_id: int) -> bool:
    schedules = load_schedules()
    updated_schedules = [
        schedule for schedule in schedules
        if schedule["id"] != schedule_id
    ]

    if len(updated_schedules) == len(schedules):
        return False

    save_schedules(updated_schedules)
    return True


# Runs all enabled scheduled tasks that are due.
# A task is considered due if it has never been run before,
# or if its configured interval has already passed.
def run_due_schedules() -> List[Dict[str, Any]]:
    schedules = load_schedules()
    results: List[Dict[str, Any]] = []
    now = datetime.now()
    updated = False

    for schedule in schedules:
        if not schedule.get("enabled", True):
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
            continue

        archive_name = create_backup(schedule["source"])
        schedule["last_run"] = now.isoformat(timespec="seconds")
        updated = True

        results.append(
            {
                "id": schedule["id"],
                "source": schedule["source"],
                "archive": archive_name,
                "run_at": schedule["last_run"],
            }
        )

    if updated:
        save_schedules(schedules)

    return results