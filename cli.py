import argparse
import logging
from app.backup import create_backup
from app.config import setup_logging
from app.restore import restore_backup
from app.scheduler import (
    add_schedule,
    delete_schedule,
    list_schedules,
    run_due_schedules,
)
from app.storage import delete_backup, list_backups


logger = logging.getLogger(__name__)
# Main entry point of the CLI application.
# This function defines all supported commands and routes them
# to the corresponding functions from the application modules.
def main() -> None:
    setup_logging()
    # Create the root CLI parser.
    parser = argparse.ArgumentParser(
        description="CLI service for backup and restore operations"
    )

    # Register subcommands.
    subparsers = parser.add_subparsers(dest="command", required=True)

    # -------------------- Backup command --------------------
    backup_parser = subparsers.add_parser(
        "backup",
        help="Create a backup of a directory"
    )
    backup_parser.add_argument(
        "source",
        help="Path to the source directory"
    )

    # -------------------- Restore command --------------------
    restore_parser = subparsers.add_parser(
        "restore",
        help="Restore a backup archive"
    )
    restore_parser.add_argument(
        "filename",
        help="Backup filename"
    )
    restore_parser.add_argument(
        "target",
        help="Path to the restore directory"
    )

    # -------------------- List backups command --------------------
    subparsers.add_parser(
        "list",
        help="List all available backups"
    )

    # -------------------- Delete backup command --------------------
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a backup archive"
    )
    delete_parser.add_argument(
        "filename",
        help="Backup filename to delete"
    )

    # -------------------- Add scheduled task command --------------------
    schedule_add_parser = subparsers.add_parser(
        "schedule-add",
        help="Add a scheduled backup task"
    )
    schedule_add_parser.add_argument(
        "source",
        help="Path to the source directory"
    )
    schedule_add_parser.add_argument(
        "interval",
        type=int,
        help="Backup interval in minutes"
    )

    # -------------------- List scheduled tasks command --------------------
    subparsers.add_parser(
        "schedule-list",
        help="List all scheduled backup tasks"
    )

    # -------------------- Delete scheduled task command --------------------
    schedule_delete_parser = subparsers.add_parser(
        "schedule-delete",
        help="Delete a scheduled backup task"
    )
    schedule_delete_parser.add_argument(
        "schedule_id",
        type=int,
        help="Scheduled task ID"
    )

    # -------------------- Run scheduler command --------------------
    subparsers.add_parser(
        "run-scheduler",
        help="Run all due scheduled backup tasks"
    )

    # Parse user input.
    args = parser.parse_args()
    logger.info("CLI command started: %s", args.command)

    try:
        if args.command == "backup":
            archive_name = create_backup(args.source)
            print(f"Backup created: {archive_name}")

        elif args.command == "restore":
            restore_path = restore_backup(args.filename, args.target)
            print(f"Backup restored to: {restore_path}")

        elif args.command == "list":
            backups = list_backups()

            if not backups:
                print("No backups found.")
            else:
                print("Available backups:")
                for backup in backups:
                    print(f"- {backup}")

        elif args.command == "delete":
            deleted = delete_backup(args.filename)

            if deleted:
                print(f"Backup deleted: {args.filename}")
            else:
                print(f"Backup not found: {args.filename}")

        elif args.command == "schedule-add":
            schedule = add_schedule(args.source, args.interval)
            print(f"Schedule added: {schedule}")

        elif args.command == "schedule-list":
            schedules = list_schedules()

            if not schedules:
                print("No scheduled tasks found.")
            else:
                print("Scheduled backup tasks:")
                for schedule in schedules:
                    print(
                        f"- ID: {schedule['id']}, "
                        f"Source: {schedule['source']}, "
                        f"Interval: {schedule['interval_minutes']} min, "
                        f"Enabled: {schedule['enabled']}, "
                        f"Last run: {schedule.get('last_run')}"
                    )

        elif args.command == "schedule-delete":
            deleted = delete_schedule(args.schedule_id)

            if deleted:
                print(f"Schedule deleted: {args.schedule_id}")
            else:
                print(f"Schedule not found: {args.schedule_id}")

        elif args.command == "run-scheduler":
            results = run_due_schedules()

            if not results:
                print("No scheduled tasks are due right now.")
            else:
                print("Executed scheduled backup tasks:")
                for result in results:
                    print(
                        f"- ID: {result['id']}, "
                        f"Source: {result['source']}, "
                        f"Archive: {result['archive']}, "
                        f"Run at: {result['run_at']}"
                    )

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()