# Canonical 1X2 feature definitions used across training and prediction pipelines.

FORM_WINDOW = 5

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

# Keys returned by compute_team_stats, mapped to feature column prefixes
HOME_OVERALL_STAT_KEYS = [
    "matches_played",
    "avg_gf",
    "avg_ga",
    "winrate",
    "ppg",
    "goal_diff",
    "clean_sheet_rate",
    "failed_to_score_rate",
]

HOME_VENUE_STAT_KEYS = HOME_OVERALL_STAT_KEYS  # same structure, home_ prefix

AWAY_OVERALL_STAT_KEYS = HOME_OVERALL_STAT_KEYS
AWAY_VENUE_STAT_KEYS = HOME_OVERALL_STAT_KEYS
