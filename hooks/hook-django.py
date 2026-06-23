# hooks/hook-django.py
import os
import django
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Forzar la ruta de Django manualmente
django_root = os.path.dirname(django.__file__)

datas = collect_data_files('django', include_py_files=True)
hiddenimports = collect_submodules('django')