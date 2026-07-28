# This script routes tool actions to the appropriate functions. It currently supports generating betting combinations based on a specified size.
# It gets called from chat_cli.py when the AI model decides to generate betting combos.
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
