# Shared configuration for live odds, predictions, and candidate filtering.

# Supported leagues (TheOddsAPI sport keys)
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

# ---------------------------------------------------------------------------
# Candidate filtering thresholds
# ---------------------------------------------------------------------------

# 1X2: preserve existing live behavior — HOME bets with edge >= 0.06
MIN_EDGE_1X2_HOME = 0.06

# BTTS / OU25: align with offline select_candidates.py defaults
MIN_EDGE_BTTS = 0.05
MIN_MODEL_PROB_BTTS = 0.45

MIN_EDGE_OU25 = 0.05
MIN_MODEL_PROB_OU25 = 0.45
