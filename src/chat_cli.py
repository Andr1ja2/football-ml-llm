import json
from llm_client import ask_model
from tool_decider import decide_intent
from tool_router import run_tool

SYSTEM_EXPLAIN_PROMPT = """
You are a football betting assistant.

You are given a betting ticket selected by a statistical system.

STRICT RULES:
- You MUST NOT invent matches, teams, odds, probabilities, or statistics.
- You MUST ONLY explain the ticket provided.
- You MUST NOT suggest alternatives.
- You MUST NOT add or remove legs.
- Risk is based ONLY on combined probability (higher probability = lower risk).
- Keep the explanation short and factual.
"""

CASUAL_CHAT_PROMPT = """
You are a polite assistant.

The user is NOT asking for betting advice.
Respond naturally and briefly.
"""

def pick_safest_combo(combos, max_legs=None):
    filtered = combos
    if max_legs is not None:
        filtered = [c for c in combos if c["n_legs"] <= max_legs]

    if not filtered:
        return None

    return max(filtered, key=lambda c: c["combo_prob"])

def main():
    print("=== Tool-Aware Betting Chat (Mistral) ===")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            break

        intent = decide_intent(user_input)

        if intent == "CASUAL_CHAT":
            response = ask_model(
                f"{CASUAL_CHAT_PROMPT}\nUser: {user_input}\nAnswer:"
            )
            print("\nMistral:\n")
            print(response.strip())
            print("-" * 60)
            continue

        if intent == "MATCH_QUERY":
            print("\nMistral:\n")
            print("I don't have data for that match.")
            print("-" * 60)
            continue

        tool_result = run_tool("GENERATE_COMBOS")

        if tool_result.get("status") != "ok" or not tool_result.get("combos"):
            print("\nMistral:\n")
            print("I don't have enough data to generate betting advice right now.")
            print("-" * 60)
            continue

        combos = tool_result["combos"]

        # Decide safest combo (deterministic)
        safest = pick_safest_combo(combos)

        if safest is None:
            print("\nMistral:\n")
            print("No suitable low-risk combo found.")
            print("-" * 60)
            continue

        payload = {
            "selected_ticket": safest
        }

        explain_prompt = f"""
{SYSTEM_EXPLAIN_PROMPT}

Ticket data:
{json.dumps(payload, indent=2)}

User request:
{user_input}

Explain this ticket and its risk level.
"""

        response = ask_model(explain_prompt)

        print("\nMistral:\n")
        print(response.strip())
        print("-" * 60)


if __name__ == "__main__":
    main()
