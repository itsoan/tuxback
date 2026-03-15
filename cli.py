import argparse
import logging

# Импорт основных модулей приложения. Каждый модуль отвечает за отдельную часть логики системы
from app.backup import create_backup
from app.config import APP_NAME, APP_VERSION, setup_logging
from app.restore import restore_backup
from app.scheduler import (
    add_schedule,
    delete_schedule,
    list_schedules,
    run_due_schedules,
)
from app.storage import delete_backup, list_backups

# Получаем logger текущего модуля
logger = logging.getLogger(__name__)

# Главная точка входа CLI приложения
def main() -> None:
    # Настраиваем систему логированияПосле этого все действия CLI будут записываться в tuxback.log
    setup_logging()

    # Создаем основной CLI parser. argparse отвечает за обработку аргументов командной строки
    parser = argparse.ArgumentParser(
        description="CLI service for backup and restore operations"
    )

    # Добавляем глобальный аргумент версии приложения
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {APP_VERSION}",
    )
    # Создаем контейнер для подкоманд CLI
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Команда: backup Создает резервную копию указанной директории
    backup_parser = subparsers.add_parser(
        "backup",
        help="Create a backup of a directory"
    )
    backup_parser.add_argument(
        "source",
        help="Path to the source directory"
    )
    # Команда: restore - восстанавливает архив в указанную директорию
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
    # Команда: list - показывает список всех архивов резервных копий
    subparsers.add_parser(
        "list",
        help="List all available backups"
    )
    # Команда: status - показывает общий статус проекта
    subparsers.add_parser(
        "status",
        help="Show project status summary"
    )
    # Команда: delete - Удаляет архив резервной копии
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a backup archive"
    )
    delete_parser.add_argument(
        "filename",
        help="Backup filename to delete"
    )
    # Команда: schedule-add - добавляет задачу планировщика
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

    # Команда: schedule-list - Показывает список всех задач планировщика
    subparsers.add_parser(
        "schedule-list",
        help="List all scheduled backup tasks"
    )

    # Команда: schedule-delete - Удаляет задачу планировщика
    schedule_delete_parser = subparsers.add_parser(
        "schedule-delete",
        help="Delete a scheduled backup task"
    )

    schedule_delete_parser.add_argument(
        "schedule_id",
        type=int,
        help="Scheduled task ID"
    )

    # Команда: run-scheduler - запускает планировщик вручную и используется systemd timer
    subparsers.add_parser(
        "run-scheduler",
        help="Run all due scheduled backup tasks"
    )

    # Парсим аргументы CLI
    args = parser.parse_args()

    # Логируем какую команду вызвал пользователь
    logger.info("CLI command started: %s", args.command)

    try:

        # backup
        if args.command == "backup":
            archive_name = create_backup(args.source)
            print(f"Backup created: {archive_name}")

        # Восстановление
        elif args.command == "restore":
            restore_path = restore_backup(args.filename, args.target)
            print(f"Backup restored to: {restore_path}")

        # Лист бэкапов
        elif args.command == "list":
            backups = list_backups()

            if not backups:
                print("No backups found.")
            else:
                print("Available backups:")
                for backup in backups:
                    print(f"- {backup}")

        # Текущий статус
        elif args.command == "status":
            backups = list_backups()
            schedules = list_schedules()

            # считаем включенные задачи
            enabled_schedules = [
                schedule for schedule in schedules if schedule.get("enabled", True)
            ]

            print(f"{APP_NAME} status:")
            print(f"- Version: {APP_VERSION}")
            print(f"- Total backups: {len(backups)}")
            print(f"- Total schedules: {len(schedules)}")
            print(f"- Enabled schedules: {len(enabled_schedules)}")

        # Удаление backup
        elif args.command == "delete":
            deleted = delete_backup(args.filename)

            if deleted:
                print(f"Backup deleted: {args.filename}")
            else:
                print(f"Backup not found: {args.filename}")

        # Добавления scheduler
        elif args.command == "schedule-add":
            schedule = add_schedule(args.source, args.interval)
            print(f"Schedule added: {schedule}")

        # Спиcок scheduler
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

        # Удаления scheduler
        elif args.command == "schedule-delete":
            deleted = delete_schedule(args.schedule_id)

            if deleted:
                print(f"Schedule deleted: {args.schedule_id}")
            else:
                print(f"Schedule not found: {args.schedule_id}")

        # Запуск scheduler 
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

    # Глобальная обработка ошибок CLI
    except Exception as error:
        logger.exception("CLI command failed")
        print(f"Error: {error}")


# Если файл запускается напрямую — запускаем CLI
if __name__ == "__main__":
    main()