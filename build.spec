
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add source directory to path
sys.path.insert(0, str(Path('.').absolute()))

a = Analysis(
    ['src/opsydian/__main__.py'],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=['opsydian', 'opsydian.cli', 'opsydian.prompts'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='opsydian',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
