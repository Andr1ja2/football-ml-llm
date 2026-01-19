import json
from run_combo_engine import main as generate_combos

ALLOWED_ACTIONS = {
    "GENERATE_COMBOS",
    "NONE"
}

def run_tool(action, args=None):
    if action == "GENERATE_COMBOS":
        combos = generate_combos(return_objects=True)
        return {
            "status": "ok",
            "combos": combos[:10]  # limit context
        }

    return {
        "status": "error",
        "message": "Unknown action"
    }
