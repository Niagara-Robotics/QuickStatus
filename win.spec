# -*- mode: python ; coding: utf-8 -*-

version = "1.0.0-beta1"
icon_file = "resources/icons/icon.ico"

a = Analysis(
    ['__main__.py'],
    pathex=[],
    binaries=[],
    datas=[(icon_file, '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f'QuickStatus-{version}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file
)
app = BUNDLE(
    exe,
    name='__main__.app',
    icon=None,
    bundle_identifier=None,
)