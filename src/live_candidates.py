# Unified live candidate pipeline for 1X2, BTTS, and OU 2.5 markets.

from __future__ import annotations

from live_odds import fetch_live_matches
from live_predict_1x2 import fetch_candidates as fetch_1x2
from live_predict_btts import fetch_candidates as fetch_btts
from live_predict_ou25 import fetch_candidates as fetch_ou25


def _dedupe_candidates(candidates: list[dict]) -> list[dict]:
    """Remove duplicate candidates for the same match/market/outcome."""
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict] = []

    for c in candidates:
        key = (c["match"], c["market"], c["outcome"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)

    return unique


def get_live_candidates() -> list[dict]:
    """
    Fetch live odds once, run all three prediction pipelines, and return
    a unified list of value candidates across 1X2, BTTS, and OU 2.5.
    """
    matches = fetch_live_matches()

    candidates: list[dict] = []
    candidates.extend(fetch_1x2(matches))
    candidates.extend(fetch_btts(matches))
    candidates.extend(fetch_ou25(matches))

    candidates = _dedupe_candidates(candidates)
    return sorted(candidates, key=lambda x: x.get("edge", 0), reverse=True)
