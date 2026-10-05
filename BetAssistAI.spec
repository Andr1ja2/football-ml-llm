from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


ROOT = Path(SPECPATH)
hiddenimports=collect_submodules("sklearn")

datas = [
    (
        str(ROOT / "data" / "processed" / "model_1x2.pkl"),
        "data/processed",
    ),
    (
        str(ROOT / "data" / "processed" / "model_btts.pkl"),
        "data/processed",
    ),
    (
        str(ROOT / "data" / "processed" / "model_ou25.pkl"),
        "data/processed",
    ),
    (
        str(ROOT / "data" / "db.sqlite"),
        "data",
    ),
]


a = Analysis(
    ["gui/main.py"],
    pathex=[
        str(ROOT),
        str(ROOT / "src"),
        str(ROOT / "gui"),
    ],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.zipfiles,
    name="BetAssistAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
