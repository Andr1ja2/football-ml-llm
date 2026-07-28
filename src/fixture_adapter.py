from live_candidates import get_live_candidates

def load_fixtures(source="live"):
    # Adapter used by the combo engine
    # Returns live betting candidates instead of mock fixtures

    if source == "live":
        candidates = get_live_candidates()

        return {
            "fixtures": candidates,
            "models": {}
        }

    raise ValueError("Unknown fixture source")
