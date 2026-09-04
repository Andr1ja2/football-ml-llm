# Sample TheOddsAPI responses for unit tests (no real API calls needed).

SAMPLE_MATCH = {
    "id": "abc123",
    "sport_key": "soccer_epl",
    "commence_time": "2026-09-05T15:00:00Z",
    "home_team": "Arsenal",
    "away_team": "Chelsea",
    "bookmakers": [
        {
            "key": "pinnacle",
            "title": "Pinnacle",
            "markets": [
                {
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Arsenal", "price": 2.10},
                        {"name": "Chelsea", "price": 3.50},
                        {"name": "Draw", "price": 3.40},
                    ],
                },
                {
                    "key": "btts",
                    "outcomes": [
                        {"name": "Yes", "price": 1.80},
                        {"name": "No", "price": 2.00},
                    ],
                },
                {
                    "key": "totals",
                    "outcomes": [
                        {"name": "Over", "price": 1.90, "point": 2.5},
                        {"name": "Under", "price": 1.95, "point": 2.5},
                        {"name": "Over", "price": 1.30, "point": 1.5},
                        {"name": "Under", "price": 3.50, "point": 1.5},
                    ],
                },
            ],
        }
    ],
}

SAMPLE_MATCH_NO_BTTS = {
    "id": "def456",
    "sport_key": "soccer_epl",
    "commence_time": "2026-09-06T15:00:00Z",
    "home_team": "Liverpool",
    "away_team": "Everton",
    "bookmakers": [
        {
            "key": "pinnacle",
            "title": "Pinnacle",
            "markets": [
                {
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Liverpool", "price": 1.50},
                        {"name": "Everton", "price": 6.00},
                        {"name": "Draw", "price": 4.50},
                    ],
                },
                {
                    "key": "totals",
                    "outcomes": [
                        {"name": "Over", "price": 1.75, "point": 2.5},
                        {"name": "Under", "price": 2.10, "point": 2.5},
                    ],
                },
            ],
        }
    ],
}

SAMPLE_MATCH_NO_BOOKMAKERS = {
    "id": "ghi789",
    "sport_key": "soccer_epl",
    "commence_time": "2026-09-07T15:00:00Z",
    "home_team": "Fulham",
    "away_team": "Brentford",
    "bookmakers": [],
}
