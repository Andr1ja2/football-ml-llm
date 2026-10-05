# Fetch and parse live bookmaker odds from TheOddsAPI for 1X2, BTTS, and OU 2.5.

from __future__ import annotations

import json
import os
from typing import Any

import requests
from dotenv import load_dotenv

try:
    from src.live_config import (
        BASE_URL,
        ODDS_FORMAT,
        ODDS_MARKETS,
        ODDS_REGIONS,
        OU25_POINT,
        SPORTS,
        settings_manager,
    )
except ModuleNotFoundError:
    from live_config import (
        BASE_URL,
        ODDS_FORMAT,
        ODDS_MARKETS,
        ODDS_REGIONS,
        OU25_POINT,
        SPORTS,
        settings_manager,
    )

load_dotenv()

REQUEST_TIMEOUT_SEC = 30

_last_fetch_error: str | None = None


def get_odds_fetch_error() -> str | None:
    return _last_fetch_error


def get_odds_api_key() -> str:
    # Try to get odds API key from settings, if not then fall back to env
    stored = (settings_manager.get("ODDS_API_KEY") or "").strip()
    if stored:
        return stored
    return (os.getenv("ODDS_API_KEY") or "").strip()


def _set_fetch_error(message: str | None) -> None:
    global _last_fetch_error
    _last_fetch_error = message


def _api_error_message(status_code: int, body: str) -> str:
    if status_code == 401:
        return (
            "TheOddsAPI rejected your API key (401 Unauthorized). "
            "Open Settings and verify your TheOddsAPI key."
        )
    if status_code == 429:
        return (
            "TheOddsAPI rate limit was exceeded (429). "
            "Wait a moment and try again, or check your plan usage on the-odds-api.com."
        )
    if status_code in (402, 403):
        return (
            "TheOddsAPI denied the request (out of credits or forbidden). "
            "Check your subscription and remaining quota on the-odds-api.com."
        )
    detail = ""
    try:
        payload = json.loads(body)
        if isinstance(payload, dict):
            detail = payload.get("message") or payload.get("error") or ""
    except json.JSONDecodeError:
        detail = body.strip()[:160] if body else ""
    if detail:
        return f"TheOddsAPI error ({status_code}): {detail}"
    return f"TheOddsAPI request failed with HTTP {status_code}."


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
    # Parse 1X2 odds into outcome
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
    # Parse BTTS odds. Outcomes are Yes/No from the API
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
    # Parse Over/Under totals for a specific line (default 2.5)
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
    # Convert decimal odds to margin-normalized implied probabilities
    raw = {k: decimal_to_prob(v) for k, v in prices.items()}
    normalized = normalize_probs(list(raw.values()))
    return dict(zip(raw.keys(), normalized))


def parse_match_odds(match: dict) -> dict[str, Any] | None:
    # Extract parsed odds for one match from a TheOddsAPI event payload
    # Use the first bookmaker, return None when no bookmaker is available
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
    rather than causing failures. User-facing errors are available via get_odds_fetch_error().
    """
    _set_fetch_error(None)

    api_key = get_odds_api_key()
    if not api_key:
        _set_fetch_error(
            "No TheOddsAPI key configured. Open Settings and enter your API key from the-odds-api.com."
        )
        return []

    http = session or requests
    all_matches: list[dict[str, Any]] = []
    errors: list[str] = []

    for sport in SPORTS:
        url = BASE_URL.format(sport=sport)
        params = {
            "apiKey": api_key,
            "regions": ODDS_REGIONS,
            "markets": ODDS_MARKETS,
            "oddsFormat": ODDS_FORMAT,
        }

        try:
            resp = http.get(url, params=params, timeout=REQUEST_TIMEOUT_SEC)
        except requests.Timeout:
            errors.append(
                f"Request timed out while fetching odds for {sport}. Check your network and try again."
            )
            continue
        except requests.RequestException as exc:
            errors.append(f"Network error while fetching odds for {sport}: {exc}")
            continue

        if resp.status_code != 200:
            errors.append(_api_error_message(resp.status_code, resp.text))
            continue

        try:
            payload = resp.json()
        except json.JSONDecodeError:
            errors.append(f"Unexpected response from TheOddsAPI for {sport} (invalid JSON).")
            continue

        if not isinstance(payload, list):
            errors.append(f"Unexpected response from TheOddsAPI for {sport}.")
            continue

        for match in payload:
            parsed = parse_match_odds(match)
            if parsed is not None:
                all_matches.append(parsed)

    if all_matches:
        _set_fetch_error(None)
        return all_matches

    if errors:
        # Prefer auth/quota messages over generic network noise.
        for err in errors:
            if "401" in err or "Unauthorized" in err:
                _set_fetch_error(err)
                return []
        _set_fetch_error(errors[0])
    else:
        _set_fetch_error(
            "No live matches with odds were returned. There may be no upcoming fixtures "
            "in the configured leagues right now."
        )

    return []
