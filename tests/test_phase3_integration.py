import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import pytest
from unittest.mock import patch
from live_candidates import get_live_candidates
from combo_engine import build_combos

# Sample data for mocking
MOCK_MATCHES = [
    {
        "match_id": "1",
        "home_team": "Team A",
        "away_team": "Team B",
        "match": "Team A vs Team B",
        "h2h": {"HOME": 2.0, "DRAW": 3.2, "AWAY": 4.0},
        "btts": {"YES": 1.8, "NO": 2.0},
        "totals": {"OVER": 1.9, "UNDER": 1.9},
    },
    {
        "match_id": "2",
        "home_team": "Team C",
        "away_team": "Team D",
        "match": "Team C vs Team D",
        "h2h": {"HOME": 1.5, "DRAW": 3.5, "AWAY": 6.0},
        "btts": {"YES": 2.1, "NO": 1.7},
        "totals": {"OVER": 2.1, "UNDER": 1.7},
    },
]

MOCK_CANDIDATES_1X2 = [
    {
        "match": "Team A vs Team B",
        "market": "1X2",
        "outcome": "HOME",
        "model_prob": 0.6,
        "book_prob": 0.5,
        "odds": 2.0,
        "edge": 0.1,
        "ev": 0.2,
    },
    {
        "match": "Team C vs Team D",
        "market": "1X2",
        "outcome": "HOME",
        "model_prob": 0.7,
        "book_prob": 0.6,
        "odds": 1.5,
        "edge": 0.1,
        "ev": 0.05,
    },
]

MOCK_CANDIDATES_BTTS = [
    {
        "match": "Team A vs Team B",
        "market": "BTTS",
        "outcome": "YES",
        "model_prob": 0.6,
        "book_prob": 0.55,
        "odds": 1.8,
        "edge": 0.05,
        "ev": 0.08,
    },
]

MOCK_CANDIDATES_OU25 = [
    {
        "match": "Team C vs Team D",
        "market": "OU25",
        "outcome": "OVER",
        "model_prob": 0.6,
        "book_prob": 0.45,
        "odds": 2.1,
        "edge": 0.15,
        "ev": 0.26,
    },
]

@patch("live_candidates.fetch_live_matches")
@patch("live_candidates.fetch_1x2")
@patch("live_candidates.fetch_btts")
@patch("live_candidates.fetch_ou25")
def test_pipeline_flow(mock_ou, mock_btts, mock_1x2, mock_matches):
    # Setup mocks
    mock_matches.return_value = MOCK_MATCHES
    mock_1x2.return_value = MOCK_CANDIDATES_1X2
    mock_btts.return_value = MOCK_CANDIDATES_BTTS
    mock_ou.return_value = MOCK_CANDIDATES_OU25

    # 1. Unified Candidates Generation
    candidates = get_live_candidates()

    # Verify unified candidates
    assert len(candidates) == len(MOCK_CANDIDATES_1X2) + len(MOCK_CANDIDATES_BTTS) + len(MOCK_CANDIDATES_OU25)
    markets = {c["market"] for c in candidates}
    assert markets == {"1X2", "BTTS", "OU25"}, "All three markets should produce candidates"

    for c in candidates:
        assert "odds" in c and c["odds"] > 0, f"Candidate {c} should contain real decimal odds"

    # 2. Combo Engine - Build 2-leg combos
    combos = build_combos(candidates, requested_size=2)

    assert len(combos) > 0, "Should produce some combos"

    for combo in combos:
        # Verify no two legs from same match
        matches = [leg["match"] for leg in combo["legs"]]
        assert len(matches) == len(set(matches)), f"Combo should not have two legs from same match: {matches}"

        # Verify probability, odds, and EV
        prob = combo["combo_prob"]
        odds = combo["combo_odds"]
        ev = combo["expected_value"]

        # Recalculate
        expected_prob = 1.0
        expected_odds = 1.0
        for leg in combo["legs"]:
            expected_prob *= leg["model_prob"]
            expected_odds *= leg["odds"]

        assert prob == round(expected_prob, 4)
        assert odds == round(expected_odds, 2)
        assert ev == round(expected_prob * expected_odds - 1.0, 3)

    # 3. Verify mixed-market combos work
    # We expect some combos to have legs from different markets
    mixed_found = False
    for combo in combos:
        markets = {leg["market"] for leg in combo["legs"]}
        if len(markets) > 1:
            mixed_found = True
            break
    assert mixed_found, "Mixed-market combos should be produced"

def test_combo_ev_calculation():
    # Basic sanity check for EV
    from combo_engine import combo_ev
    assert combo_ev(0.6, 2.0) == pytest.approx(0.2)
    assert combo_ev(0.4, 1.5) == pytest.approx(-0.4)
