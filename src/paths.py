# Centralizes file paths so the app works correctly both during development and when packaged with PyInstaller.

import sys
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent.parent

if getattr(sys, "frozen", False):
    BUNDLE_ROOT = Path(sys._MEIPASS)
    APP_ROOT = Path(sys.executable).resolve().parent
else:
    BUNDLE_ROOT = SOURCE_ROOT
    APP_ROOT = SOURCE_ROOT

MODEL_DIR = BUNDLE_ROOT / "data" / "processed"

SETTINGS_PATH = APP_ROOT / "settings.json"

DB_PATH = APP_ROOT / "data" / "db.sqlite"
DB_TEMPLATE_PATH = BUNDLE_ROOT / "data" / "db.sqlite"