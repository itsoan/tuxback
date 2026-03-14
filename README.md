# TuxBack

TuxBack is a CLI-based backup and restore service for Linux, developed in Python.
The project is designed to create, store, restore, and manage backup archives, and also supports scheduled backup task configuration.

## Features

- Create backups of directories in `.tar.gz` format
- Restore data from backup archives
- View the list of available backups
- Delete backup archives
- Add, view, and delete scheduled backup tasks
- Run the application locally or inside Docker

## Project Structure

```text
tuxback/
├── app/
│   ├── __init__.py
│   ├── backup.py
│   ├── config.py
│   ├── restore.py
│   ├── scheduler.py
│   └── storage.py
├── backups/
├── cli.py
├── Dockerfile
├── requirements.txt
├── README.md
└── schedules.json