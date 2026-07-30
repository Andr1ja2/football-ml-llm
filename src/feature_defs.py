# Canonical feature definitions used across training and prediction pipelines.

FORM_WINDOW = 5

# ---------------------------------------------------------------------------
# 1X2 features (full-time result: home / draw / away)
# ---------------------------------------------------------------------------

# Bookmaker implied probabilities (margin-normalized)
BOOKMAKER_FEATURES = [
    "home_prob",
    "draw_prob",
    "away_prob",
]

# Overall rolling form (last FORM_WINDOW matches, any venue)
HOME_OVERALL_FORM = [
    "home_matches_played",
    "home_avg_gf",
    "home_avg_ga",
    "home_winrate",
    "home_ppg",
    "home_goal_diff",
    "home_clean_sheet_rate",
    "home_failed_to_score_rate",
]

AWAY_OVERALL_FORM = [
    "away_matches_played",
    "away_avg_gf",
    "away_avg_ga",
    "away_winrate",
    "away_ppg",
    "away_goal_diff",
    "away_clean_sheet_rate",
    "away_failed_to_score_rate",
]

# Venue-specific rolling form (home team at home, away team away)
HOME_VENUE_FORM = [
    "home_home_matches_played",
    "home_home_avg_gf",
    "home_home_avg_ga",
    "home_home_winrate",
    "home_home_ppg",
    "home_home_goal_diff",
    "home_home_clean_sheet_rate",
    "home_home_failed_to_score_rate",
]

AWAY_VENUE_FORM = [
    "away_away_matches_played",
    "away_away_avg_gf",
    "away_away_avg_ga",
    "away_away_winrate",
    "away_away_ppg",
    "away_away_goal_diff",
    "away_away_clean_sheet_rate",
    "away_away_failed_to_score_rate",
]

STRENGTH_FEATURES = [
    "home_attack_strength",
    "home_defense_strength",
    "away_attack_strength",
    "away_defense_strength",
]

FEATURE_COLS_1X2: list[str] = (
    BOOKMAKER_FEATURES
    + HOME_OVERALL_FORM
    + HOME_VENUE_FORM
    + AWAY_OVERALL_FORM
    + AWAY_VENUE_FORM
    + STRENGTH_FEATURES
)

# ---------------------------------------------------------------------------
# BTTS / Over-Under 2.5 features (goal-related)
# ---------------------------------------------------------------------------

# Rolling form per team, goal-only view. Reused for both BTTS and OU 2.5 so
# the two models share a single source of truth.
HOME_GOAL_FORM = [
    "home_btts_rate",
    "home_avg_goals",
    "home_avg_goals_for",
    "home_avg_goals_against",
    "home_clean_sheet_rate",
    "home_failed_to_score_rate",
    "home_goal_diff",
    "home_ppg",
    "home_attack_strength",
    "home_defense_strength",
    "home_goals_last5",
    "home_scored_rate_last5",
    "home_goals_conceded_last5",
    "home_conceded_rate_last5",
    "home_goal_std",
]

AWAY_GOAL_FORM = [
    "away_btts_rate",
    "away_avg_goals",
    "away_avg_goals_for",
    "away_avg_goals_against",
    "away_clean_sheet_rate",
    "away_failed_to_score_rate",
    "away_goal_diff",
    "away_ppg",
    "away_attack_strength",
    "away_defense_strength",
    "away_goals_last5",
    "away_scored_rate_last5",
    "away_goals_conceded_last5",
    "away_conceded_rate_last5",
    "away_goal_std",
]

FEATURE_COLS_BTTS_OU: list[str] = HOME_GOAL_FORM + AWAY_GOAL_FORM
