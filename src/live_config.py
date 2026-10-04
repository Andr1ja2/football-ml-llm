import json
import os
from pathlib import Path

SETTINGS_PATH = Path(__file__).resolve().parent.parent / "settings.json"

DEFAULT_SETTINGS = {
    "MIN_EDGE_1X2_HOME": 0.06,
    "MIN_EDGE_BTTS": 0.05,
    "MIN_MODEL_PROB_BTTS": 0.45,
    "MIN_EDGE_OU25": 0.05,
    "MIN_MODEL_PROB_OU25": 0.45,
    "MAX_LEGS": 5,
    "ASSISTANT_NAME": "모 Agent",
    "LLM_MODEL": "",
    "ODDS_API_KEY": "",
}

class SettingsManager:
    def __init__(self):
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        if SETTINGS_PATH.exists():
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    # Merge loaded settings with defaults to ensure new keys (like MAX_LEGS) are present
                    self.settings = DEFAULT_SETTINGS.copy()
                    self.settings.update(loaded_settings)
            except (json.JSONDecodeError, IOError):
                print("Error loading settings.json, using defaults.")
                self._set_defaults()
        else:
            self._set_defaults()
            self.save_settings()

    def _set_defaults(self):
        self.settings = DEFAULT_SETTINGS.copy()

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value

    def save_settings(self):
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def restore_defaults(self):
        self._set_defaults()
        self.save_settings()

# Global instance for the app
settings_manager = SettingsManager()

def __getattr__(name):
    """
    Allows modules to import constants directly from live_config.
    Example: from live_config import MIN_EDGE_BTTS

    Instead of returning a static value, this intercepts the attribute access
    and fetches the current value from SettingsManager (and settings.json).
    This allows settings changes to take effect in real-time without restarts.
    """
    return settings_manager.get(name, DEFAULT_SETTINGS.get(name))

# For explicitly defined non-dynamic constants
SPORTS = [
    "soccer_epl",
    "soccer_germany_bundesliga",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
]

BASE_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds"
ODDS_REGIONS = "eu"
ODDS_FORMAT = "decimal"
ODDS_MARKETS = "h2h,totals"
OU25_POINT = 2.5
