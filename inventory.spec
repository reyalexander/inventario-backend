# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, copy_metadata

project_dir = Path.cwd()
os.environ["DJANGO_SETTINGS_MODULE"] = "inventory.settings_desktop"

block_cipher = None

hiddenimports = []

hiddenimports += [
    "inventory.settings_desktop",
    "environ",
    "environ.environ",

    "corsheaders",
    "corsheaders.middleware",
    "corsheaders.defaults",

    "django_filters",
    "django_filters.rest_framework",

    "rest_framework",
    "rest_framework.authentication",
    "rest_framework.decorators",
    "rest_framework.exceptions",
    "rest_framework.fields",
    "rest_framework.filters",
    "rest_framework.mixins",
    "rest_framework.negotiation",
    "rest_framework.pagination",
    "rest_framework.parsers",
    "rest_framework.permissions",
    "rest_framework.renderers",
    "rest_framework.response",
    "rest_framework.routers",
    "rest_framework.schemas",
    "rest_framework.schemas.openapi",
    "rest_framework.serializers",
    "rest_framework.settings",
    "rest_framework.status",
    "rest_framework.validators",
    "rest_framework.viewsets",
    "rest_framework.views",

    "rest_framework_simplejwt",
    "rest_framework_simplejwt.authentication",
]

hiddenimports += collect_submodules("barcode")
hiddenimports += collect_submodules("reportlab.graphics.barcode")
hiddenimports += collect_submodules("xhtml2pdf")
hiddenimports += collect_submodules("rest_framework")
hiddenimports += collect_submodules("rest_framework_simplejwt")

datas = [
    (str(project_dir / "inventory"), "inventory"),
    (str(project_dir / "apps"), "apps"),
    (str(project_dir / "staticfiles"), "staticfiles"),
    (str(project_dir / "data"), "data"),
    (str(project_dir / ".env.desktop"), "."),
]

datas += collect_data_files("barcode")
datas += collect_data_files("reportlab")
datas += collect_data_files("environ")
datas += collect_data_files("xhtml2pdf")

datas += copy_metadata("Django")
datas += copy_metadata("djangorestframework")
datas += copy_metadata("django-filter")
datas += copy_metadata("django-environ")
datas += copy_metadata("python-barcode")
datas += copy_metadata("reportlab")
datas += copy_metadata("xhtml2pdf")

a = Analysis(
    ["run_desktop.py"],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[str(project_dir / "hooks")],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "drf_yasg",
        "django.contrib.postgres",
        "psycopg2",
        "psycopg",
        "cx_Freeze",
        "coreapi",
        "coreschema",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="inventory_backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="inventory_backend",
)