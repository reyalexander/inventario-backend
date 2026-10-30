import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
else:
    BASE_DIR = Path(__file__).resolve().parent

if sys.platform == "darwin":
    DATA_DIR = Path.home() / "Library" / "Application Support" / "Elegant Lady"
else:
    DATA_DIR = BASE_DIR / "data"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory.settings_desktop")


def ensure_directories():
    data_dir = DATA_DIR
    media_dir = data_dir / "media"

    data_dir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)


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
