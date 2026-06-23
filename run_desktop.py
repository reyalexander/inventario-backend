import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory.settings_desktop")


def ensure_directories():
    data_dir = BASE_DIR / "data"
    media_dir = data_dir / "media"
    static_dir = BASE_DIR / "staticfiles"

    data_dir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)


def main():
    ensure_directories()

    from django.core.management import execute_from_command_line

    # aplica migraciones automáticamente
    execute_from_command_line([
        "manage.py",
        "migrate",
        "--noinput",
    ])

    # luego levanta servidor
    execute_from_command_line([
        "manage.py",
        "runserver",
        "127.0.0.1:8001",
        "--noreload",
    ])


if __name__ == "__main__":
    main()