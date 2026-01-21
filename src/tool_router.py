from run_combo_engine import main as generate_combos

def run_tool(action, args=None):
    if action == "GENERATE_COMBOS":
        size = args.get("size", 3)
        combos, was_capped = generate_combos(size, return_objects=True)
        return {
            "status": "ok",
            "combos": combos,
            "was_capped": was_capped,
            "size": min(size, 5)
        }

    return {"status": "error"}
