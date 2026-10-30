#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess
from pathlib import Path


def use_project_venv():
    """Use the project interpreter when Git Bash resolves `python` to Conda."""
    if os.name != 'nt':
        return
    venv_python = Path(__file__).resolve().parent / 'venv' / 'Scripts' / 'python.exe'
    if venv_python.is_file() and os.path.normcase(sys.executable) != os.path.normcase(str(venv_python)):
        raise SystemExit(subprocess.call([str(venv_python), __file__, *sys.argv[1:]]))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if len(sys.argv) == 1:
    sys.argv += ['runserver', '0.0.0.0:8001']
elif len(sys.argv) == 2 and sys.argv[1] == 'runserver':
    sys.argv.append('0.0.0.0:8001')

if __name__ == '__main__':
    use_project_venv()
    main()
