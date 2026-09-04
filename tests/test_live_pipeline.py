"""Smoke tests for Phase 3 live odds, candidates, and combo engine."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from combo_engine import build_combos, combo_ev, combo_odds, combo_probability
from live_odds import (
    decimal_to_prob,
    normalize_probs,
    parse_btts_market,
    parse_h2h_market,
    parse_match_odds,
    parse_totals_market,
    prices_to_book_probs,
)
from tests.fixtures.sample_odds import (
    SAMPLE_MATCH,
    SAMPLE_MATCH_NO_BOOKMAKERS,
    SAMPLE_MATCH_NO_BTTS,
)


class TestOddsParsing(unittest.TestCase):
    def test_decimal_to_prob(self):
        self.assertAlmostEqual(decimal_to_prob(2.0), 0.5)
        self.assertEqual(decimal_to_prob(0), 0.0)

    def test_normalize_probs(self):
        result = normalize_probs([0.5, 0.3, 0.2])
        self.assertAlmostEqual(sum(result), 1.0)

    def test_parse_h2h_market(self):
        market = SAMPLE_MATCH["bookmakers"][0]["markets"][0]
        prices = parse_h2h_market(market, "Arsenal", "Chelsea")
        self.assertIsNotNone(prices)
        self.assertIn("HOME", prices)
        self.assertIn("DRAW", prices)
        self.assertIn("AWAY", prices)
        self.assertEqual(prices["HOME"], 2.10)

    def test_parse_btts_market(self):
        market = SAMPLE_MATCH["bookmakers"][0]["markets"][1]
        prices = parse_btts_market(market)
        self.assertIsNotNone(prices)
        self.assertEqual(prices["YES"], 1.80)
        self.assertEqual(prices["NO"], 2.00)

    def test_parse_totals_market_filters_25(self):
        market = SAMPLE_MATCH["bookmakers"][0]["markets"][2]
        prices = parse_totals_market(market, point=2.5)
        self.assertIsNotNone(prices)
        self.assertEqual(prices["OVER"], 1.90)
        self.assertEqual(prices["UNDER"], 1.95)

    def test_parse_totals_market_missing_line(self):
        market = {"key": "totals", "outcomes": [
            {"name": "Over", "price": 1.30, "point": 1.5},
            {"name": "Under", "price": 3.50, "point": 1.5},
        ]}
        self.assertIsNone(parse_totals_market(market, point=2.5))

    def test_prices_to_book_probs(self):
        probs = prices_to_book_probs({"YES": 1.80, "NO": 2.00})
        self.assertAlmostEqual(sum(probs.values()), 1.0)
        self.assertGreater(probs["YES"], probs["NO"])

    def test_parse_match_odds_full(self):
        parsed = parse_match_odds(SAMPLE_MATCH)
        self.assertIsNotNone(parsed)
        self.assertIsNotNone(parsed["h2h"])
        self.assertIsNotNone(parsed["btts"])
        self.assertIsNotNone(parsed["totals"])
        self.assertEqual(parsed["match"], "Arsenal vs Chelsea")

    def test_parse_match_odds_missing_btts(self):
        parsed = parse_match_odds(SAMPLE_MATCH_NO_BTTS)
        self.assertIsNotNone(parsed)
        self.assertIsNotNone(parsed["h2h"])
        self.assertIsNone(parsed["btts"])
        self.assertIsNotNone(parsed["totals"])

    def test_parse_match_odds_no_bookmakers(self):
        self.assertIsNone(parse_match_odds(SAMPLE_MATCH_NO_BOOKMAKERS))


class TestCandidateCreation(unittest.TestCase):
    def _make_candidate(self, match, market, outcome, model_prob, book_prob, odds):
        return {
            "match": match,
            "market": market,
            "outcome": outcome,
            "model_prob": model_prob,
            "book_prob": book_prob,
            "odds": odds,
            "edge": model_prob - book_prob,
            "ev": model_prob * odds - 1.0,
        }

    def test_ev_calculation(self):
        c = self._make_candidate("A vs B", "BTTS", "YES", 0.60, 0.50, 1.80)
        self.assertAlmostEqual(c["ev"], 0.60 * 1.80 - 1.0)

    def test_edge_calculation(self):
        c = self._make_candidate("A vs B", "OU25", "OVER", 0.55, 0.48, 1.90)
        self.assertAlmostEqual(c["edge"], 0.07)


class TestComboEngine(unittest.TestCase):
    def _leg(self, match, market, outcome, model_prob, book_prob, odds):
        return {
            "match": match,
            "market": market,
            "outcome": outcome,
            "model_prob": model_prob,
            "book_prob": book_prob,
            "odds": odds,
            "edge": model_prob - book_prob,
        }

    def test_combo_probability_independence(self):
        legs = [
            self._leg("A vs B", "1X2", "HOME", 0.50, 0.40, 2.5),
            self._leg("C vs D", "BTTS", "YES", 0.60, 0.50, 1.8),
        ]
        self.assertAlmostEqual(combo_probability(legs), 0.30)

    def test_combo_odds_from_decimal(self):
        legs = [
            self._leg("A vs B", "1X2", "HOME", 0.50, 0.40, 2.0),
            self._leg("C vs D", "BTTS", "YES", 0.60, 0.50, 1.5),
        ]
        self.assertAlmostEqual(combo_odds(legs), 3.0)

    def test_combo_ev(self):
        self.assertAlmostEqual(combo_ev(0.30, 3.0), -0.10)

    def test_same_match_exclusion(self):
        candidates = [
            self._leg("A vs B", "1X2", "HOME", 0.55, 0.40, 2.0),
            self._leg("A vs B", "BTTS", "YES", 0.60, 0.50, 1.8),
            self._leg("C vs D", "OU25", "OVER", 0.58, 0.48, 1.9),
        ]
        combos = build_combos(candidates, 2)
        for combo in combos:
            matches = [leg["match"] for leg in combo["legs"]]
            self.assertEqual(len(matches), len(set(matches)))

    def test_mixed_market_combos(self):
        candidates = [
            self._leg("A vs B", "1X2", "HOME", 0.55, 0.40, 2.0),
            self._leg("C vs D", "BTTS", "YES", 0.60, 0.50, 1.8),
            self._leg("E vs F", "OU25", "OVER", 0.58, 0.48, 1.9),
        ]
        combos = build_combos(candidates, 2)
        self.assertTrue(len(combos) > 0)
        markets = {leg["market"] for combo in combos for leg in combo["legs"]}
        self.assertTrue(len(markets) > 1)

    def test_no_duplicate_candidates_in_combo(self):
        candidates = [
            self._leg("A vs B", "1X2", "HOME", 0.55, 0.40, 2.0),
            self._leg("C vs D", "BTTS", "YES", 0.60, 0.50, 1.8),
        ]
        combos = build_combos(candidates, 2)
        self.assertEqual(len(combos), 1)


class TestMissingMarketHandling(unittest.TestCase):
    @patch("live_odds.SPORTS", ["soccer_epl"])
    @patch("live_odds.API_KEY", "test-key")
    @patch("live_odds.requests.get")
    def test_fetch_handles_api_error(self, mock_get):
        from live_odds import fetch_live_matches

        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_get.return_value = mock_resp

        matches = fetch_live_matches()
        self.assertEqual(matches, [])

    @patch("live_odds.SPORTS", ["soccer_epl"])
    @patch("live_odds.API_KEY", "test-key")
    @patch("live_odds.requests.get")
    def test_fetch_parses_response(self, mock_get):
        from live_odds import fetch_live_matches

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [SAMPLE_MATCH, SAMPLE_MATCH_NO_BTTS]
        mock_get.return_value = mock_resp

        matches = fetch_live_matches()
        self.assertEqual(len(matches), 2)
        self.assertIsNotNone(matches[0]["h2h"])
        self.assertIsNotNone(matches[0]["btts"])
        self.assertIsNone(matches[1]["btts"])


if __name__ == "__main__":
    unittest.main()
