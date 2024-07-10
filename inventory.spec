# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Collect all submodules from reportlab.graphics.barcode
hiddenimports = collect_submodules('reportlab.graphics.barcode')

block_cipher = None


a = Analysis(
    ['manage.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('inventory/settings.py', 'inventory'),
        # Include ReportLab fonts and encodings
        ('venv/Lib/site-packages/reportlab/fonts', 'reportlab/fonts'),
        ('venv/Lib/site-packages/reportlab/platypus', 'reportlab/platypus'),
        ('venv/Lib/site-packages/reportlab/pdfbase', 'reportlab/pdfbase'),
        # Include additional ReportLab barcode modules
        ('venv/Lib/site-packages/reportlab/graphics/barcode/code128.py', 'reportlab/graphics/barcode'),
        ('venv/Lib/site-packages/reportlab/graphics/barcode/code39.py', 'reportlab/graphics/barcode'),
        ('venv/Lib/site-packages/reportlab/graphics/barcode/code93.py', 'reportlab/graphics/barcode'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='inventory',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, upx_exclude=[], name='inventory')
