# Entry point for the live multi-market combo pipeline:
# live odds -> live predictions -> unified candidates -> combo engine -> ranked combos

from combo_engine import MAX_LEGS, build_combos
from live_candidates import get_live_candidates


def main(requested_size: int, return_objects: bool = False):
    was_capped = False
    if requested_size > MAX_LEGS:
        requested_size = MAX_LEGS
        was_capped = True

    candidates = get_live_candidates()
    combos = build_combos(candidates, requested_size)

    if return_objects:
        return combos, was_capped

    print(f"\nCollected {len(candidates)} live candidates "
          f"({sum(1 for c in candidates if c['market'] == '1X2')} 1X2, "
          f"{sum(1 for c in candidates if c['market'] == 'BTTS')} BTTS, "
          f"{sum(1 for c in candidates if c['market'] == 'OU25')} OU25)\n")

    if candidates:
        print("Top candidates:")
        for c in candidates[:10]:
            print(f"  [{c['market']}] {c['match']} {c['outcome']} | "
                  f"model={c['model_prob']:.3f} book={c['book_prob']:.3f} "
                  f"edge={c['edge']:.3f} ev={c.get('ev', 0):.3f} odds={c.get('odds', 0):.2f}")
        print()

    print(f"Top {requested_size}-selection combos:\n")
    if not combos:
        print("  No combos met the minimum EV/probability thresholds.")
    else:
        for c in combos[:5]:
            print(f"{c['n_legs']} selections | EV={c['expected_value']} | odds={c['combo_odds']}")
            for leg in c["legs"]:
                print(f"  - [{leg.get('market', '?')}] {leg['match']} [{leg['outcome']}] "
                      f"edge={leg['edge']}")
            print()


if __name__ == "__main__":
    main(3)
