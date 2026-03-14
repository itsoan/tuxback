# TuxBack

TuxBack is a CLI-based backup and restore service for Linux, developed in Python. The project was created as a diploma project focused on backup automation, recovery operations, Docker containerization, and CI/CD integration.

## Project Goals

The main goal of the project is to provide a simple and extensible command-line service that can:

- create compressed backups of directories;
- restore files from backup archives;
- manage backup storage;
- configure scheduled backup tasks;
- run both locally and inside Docker;
- be automatically checked through CI/CD.

## Implemented Features

- Creation of backup archives in `.tar.gz` format
- Restore of backup archives into a target directory
- Listing available backups
- Deletion of backup archives
- Adding scheduled backup tasks
- Listing scheduled backup tasks
- Deleting scheduled backup tasks
- Manual execution of due scheduled tasks
- Logging to console and file (`tuxback.log`)
- Docker image build and container launch support
- GitHub Actions CI workflow
- Safe restore validation against archive path traversal
- Executable launcher script `tuxback`
- `status` command for project summary
- `--version` flag for utility version output
- Duplicate scheduled task protection

## Project Structure

```text
tuxback/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── __init__.py
│   ├── backup.py
│   ├── config.py
│   ├── restore.py
│   ├── scheduler.py
│   └── storage.py
├── backups/
├── test_data/
├── cli.py
├── Dockerfile
├── requirements.txt
├── README.md
├── schedules.json
├── tuxback
└── tuxback.log
```
## Technologies Used

- Python 3.12
- Standard Library (`argparse`, `tarfile`, `pathlib`, `json`, `logging`, `datetime`)
- Docker
- GitHub Actions

## Local Run

Move to the project directory:

```bash
cd tuxback
```

Make the launcher executable:

```bash
chmod +x tuxback
```

Show all available commands:

```bash
./tuxback --help
```

Show utility version:

```bash
./tuxback --version
```

Create a test directory:
```bash
mkdir -p test_data
echo "hello backup" > test_data/file.txt
```

Create a backup:

```bash
./tuxback backup test_data
```

List backups:

```bash
./tuxback list
```

Show project status summary:

```bash
./tuxback status
```

Restore a backup:
```bash
./tuxback restore test_data_YYYYMMDD_HHMMSS.tar.gz restored_data
```

Delete a backup:

```bash
./tuxback delete test_data_YYYYMMDD_HHMMSS.tar.gz
```

## Optional Global Command Installation

To run the utility as a regular command from anywhere in the system, create a symbolic link:

```bash
sudo ln -sf "$(pwd)/tuxback" /usr/local/bin/tuxback
```

After that, the utility can be started like this:

```bash
tuxback --help
tuxback list
tuxback backup test_data
```
tuxback status
tuxback --version

## Scheduled Tasks

Add a scheduled backup task:

```bash
./tuxback schedule-add test_data 1
```

List scheduled tasks:
```bash
./tuxback schedule-list
```

Run all due scheduled tasks:

```bash
./tuxback run-scheduler
```
If you try to add the same active schedule with the same source and interval twice, TuxBack will reject it to prevent duplicates.


Delete a scheduled task:

```bash
./tuxback schedule-delete 1

## Logging

All main operations are logged to both the terminal and the file `tuxback.log`.

Examples:

```bash
./tuxback list
tail -n 20 tuxback.log
```

## Docker Usage

Build the image:

```bash
docker build -t tuxback .
```

Run container help:

```bash
docker run --rm tuxback
```

Run commands using the current project directory as a mounted volume:

```bash
docker run --rm -v "$(pwd):/app" tuxback ./tuxback list
docker run --rm -v "$(pwd):/app" tuxback ./tuxback backup test_data
```

## CI/CD

The project includes a GitHub Actions workflow located at:

```text
.github/workflows/ci.yml
```

The pipeline performs the following actions:

- checks out the repository;
- sets up Python 3.12;
- installs dependencies;
- makes the launcher executable;
- creates test data;
- verifies module imports;
- runs launcher-based smoke checks;
- verifies log file creation;
- builds the Docker image;
- runs the Docker container.



## Example Workflow

## Future Improvements

- remote storage support;
- encryption of backup archives;
- automatic cleanup of old backups;
- unit and integration tests;
- support for cron or systemd timer integration;
- backup configuration via environment variables.

## License

This project is distributed under the terms of the LICENSE file.