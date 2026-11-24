# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['starfield_voice_copier.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Unused and large Qt modules
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.QtQuickWidgets',
        'PySide6.QtDesigner',
        'PySide6.QtHelp',
        'PySide6.QtNetwork',
        'PySide6.QtDBus',
        'PySide6.QtTest',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        'PySide6.QtMultimedia',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.Qt3DCore',
        'PySide6.QtCharts',
        'PySide6.QtDataVisualization',
        # Unused Python modules
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='StarfieldVoiceCopier',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,          # Make sure UPX is in your PATH or System32 to use this
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,     # Equivalent to --windowed
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,         # Change to 'icon.ico' if you add an icon later
)