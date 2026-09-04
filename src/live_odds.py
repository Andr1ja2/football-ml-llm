# Fetch and parse live bookmaker odds from TheOddsAPI for 1X2, BTTS, and OU 2.5.

from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv

from live_config import (
    BASE_URL,
    ODDS_FORMAT,
    ODDS_MARKETS,
    ODDS_REGIONS,
    OU25_POINT,
    SPORTS,
)

load_dotenv()

API_KEY = os.getenv("ODDS_API_KEY")


def decimal_to_prob(odds: float) -> float:
    return 1.0 / odds if odds > 0 else 0.0


def normalize_probs(probs: list[float]) -> list[float]:
    total = sum(probs)
    if total == 0:
        return probs
    return [p / total for p in probs]


def _find_market(markets: list[dict], key: str) -> dict | None:
    for market in markets:
        if market.get("key") == key:
            return market
    return None


def parse_h2h_market(
    market: dict | None,
    home_team: str,
    away_team: str,
) -> dict[str, float] | None:
    # Parse 1X2 odds into outcome -> decimal price mapping.
    if market is None:
        return None

    outcomes = market.get("outcomes", [])
    if len(outcomes) != 3:
        return None

    prices: dict[str, float] = {}
    for outcome in outcomes:
        name = outcome["name"].lower().strip()
        if name == home_team.lower():
            prices["HOME"] = outcome["price"]
        elif name == away_team.lower():
            prices["AWAY"] = outcome["price"]
        elif name == "draw":
            prices["DRAW"] = outcome["price"]

    if len(prices) != 3:
        return None

    return prices


def parse_btts_market(market: dict | None) -> dict[str, float] | None:
    # Parse BTTS odds. Outcomes are Yes/No from the API.
    if market is None:
        return None

    prices: dict[str, float] = {}
    for outcome in market.get("outcomes", []):
        name = outcome["name"].lower().strip()
        if name == "yes":
            prices["YES"] = outcome["price"]
        elif name == "no":
            prices["NO"] = outcome["price"]

    if len(prices) != 2:
        return None

    return prices


def parse_totals_market(
    market: dict | None,
    point: float = OU25_POINT,
) -> dict[str, float] | None:
    # Parse Over/Under totals for a specific line (default 2.5).
    if market is None:
        return None

    prices: dict[str, float] = {}
    for outcome in market.get("outcomes", []):
        if outcome.get("point") != point:
            continue

        name = outcome["name"].lower().strip()
        if name == "over":
            prices["OVER"] = outcome["price"]
        elif name == "under":
            prices["UNDER"] = outcome["price"]

    if len(prices) != 2:
        return None

    return prices


def prices_to_book_probs(prices: dict[str, float]) -> dict[str, float]:
    # Convert decimal odds to margin-normalized implied probabilities.
    raw = {k: decimal_to_prob(v) for k, v in prices.items()}
    normalized = normalize_probs(list(raw.values()))
    return dict(zip(raw.keys(), normalized))


def parse_match_odds(match: dict) -> dict[str, Any] | None:
    """
    Extract parsed odds for one match from a TheOddsAPI event payload.

    Uses the first bookmaker (consistent with the existing 1X2 pipeline).
    Returns None when no bookmaker is available.
    """
    bookmakers = match.get("bookmakers") or []
    if not bookmakers:
        return None

    book = bookmakers[0]
    markets = book.get("markets", [])
    home = match["home_team"]
    away = match["away_team"]

    h2h_prices = parse_h2h_market(_find_market(markets, "h2h"), home, away)
    btts_prices = parse_btts_market(_find_market(markets, "btts"))
    totals_prices = parse_totals_market(_find_market(markets, "totals"))

    return {
        "match_id": match.get("id"),
        "home_team": home,
        "away_team": away,
        "match": f"{home} vs {away}",
        "date": match.get("commence_time"),
        "bookmaker": book.get("title") or book.get("key"),
        "h2h": h2h_prices,
        "btts": btts_prices,
        "totals": totals_prices,
    }


def fetch_live_matches(session: requests.Session | None = None) -> list[dict[str, Any]]:
    """
    Fetch upcoming matches with odds for all supported leagues.

    Missing markets (e.g. BTTS not offered by a bookmaker) are returned as None
    rather than causing failures.
    """
    if not API_KEY:
        print("Warning: ODDS_API_KEY not set; no live odds available.")
        return []

    http = session or requests
    all_matches: list[dict[str, Any]] = []

    for sport in SPORTS:
        url = BASE_URL.format(sport=sport)
        params = {
            "apiKey": API_KEY,
            "regions": ODDS_REGIONS,
            "markets": ODDS_MARKETS,
            "oddsFormat": ODDS_FORMAT,
        }

        try:
            resp = http.get(url, params=params, timeout=30)
        except requests.RequestException as exc:
            print(f"Request failed for {sport}: {exc}")
            continue

        if resp.status_code != 200:
            print(f"Failed for {sport} ({resp.status_code}): {resp.text[:200]}")
            continue

        for match in resp.json():
            parsed = parse_match_odds(match)
            if parsed is not None:
                all_matches.append(parsed)

    return all_matches
