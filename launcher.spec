# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Wallpaper Manager
# Build with: pyinstaller launcher.spec

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('api', 'api'),
        ('utils', 'utils'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        # Flask and dependencies
        'flask',
        'flask.app',
        'flask.blueprints',
        'flask.ctx',
        'flask.globals',
        'flask.helpers',
        'flask.json',
        'flask.sessions',
        'flask.signals',
        'flask.templating',
        'flask.wrappers',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.security',
        'werkzeug.routing',
        'werkzeug.exceptions',
        'jinja2',
        'jinja2.ext',
        'jinja2.loaders',
        'markupsafe',
        'itsdangerous',
        'click',
        'blinker',
        
        # Project modules
        'vdf',
        'PIL',
        'PIL.Image',
        
        # Standard library
        'json',
        'pathlib',
        'threading',
        'webbrowser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
        'pytest',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='WallpaperManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False to hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if you have one: icon='icon.ico'
)
