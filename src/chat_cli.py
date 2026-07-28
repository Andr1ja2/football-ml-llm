# This script implements a command-line interface for a tool-aware betting chat application. 
# It allows users to interact with an AI model that can either engage in casual conversation or generate football betting tickets based on user input. 
# The AI model decides the appropriate action based on the user's message and the conversation context.
# The LLM's role is to understand the user's request and decide which tool to invoke, present the results and avoid making up information.
import json
from llm_client import ask_model
from tool_decider import decide_action
from tool_router import run_tool

MAX_LEGS = 4
DEFAULT_SIZE = 3

SYSTEM_EXPLAIN_PROMPT = """
You are explaining a football betting ticket.

Use ONLY the information provided in the ticket.
Do NOT invent markets or reinterpret them.

Markets mean:

1X2:
HOME = home team wins
DRAW = match ends in draw
AWAY = away team wins

BTTS:
YES = both teams score
NO = at least one team does not score

OU25:
OVER = total goals over 2.5
UNDER = total goals under 2.5

Explain:
- the selections
- probability
- risk

Do not invent additional meaning.
"""

CASUAL_CHAT_PROMPT = """
You are a polite assistant.
The user is not asking for betting advice.
Respond naturally and briefly.
"""

def main():
    print("=== Tool-Aware Betting Chat (Mistral) ===")
    print("Type 'exit' to quit.\n")

    conversation = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        conversation.append(f"User: {user_input}")

        convo_text = "\n".join(conversation)

        decision = decide_action(user_input, convo_text)

        if decision["action"] == "CASUAL_CHAT":
            response = ask_model(
                f"{CASUAL_CHAT_PROMPT}\nUser: {user_input}\nAnswer:"
            )
            print("\nMistral:\n")
            print(response.strip())
            print("-" * 60)

            conversation.append(f"Assistant: {response.strip()}")
            continue

        requested_size = decision["params"]["size"] if decision["params"] and "size" in decision["params"] else None
        if requested_size is None:
            requested_size = DEFAULT_SIZE

        was_capped = False
        if requested_size > MAX_LEGS:
            requested_size = MAX_LEGS
            was_capped = True

        tool_result = run_tool(
            "GENERATE_COMBOS",
            args={"size": requested_size}
        )

        if tool_result.get("status") != "ok" or not tool_result.get("combos"):
            msg = "I don't have enough data to generate a betting ticket right now."
            print("\nMistral:\n")
            print(msg)
            print("-" * 60)
            conversation.append(f"Assistant: {msg}")
            continue

        if was_capped:
            info = f"Note: the maximum ticket size is {MAX_LEGS}. I generated a {MAX_LEGS}-selection ticket."
            print(f"\nMistral:\n{info}\n")

        ticket = tool_result["combos"][0]

        explain_prompt = f"""
{SYSTEM_EXPLAIN_PROMPT}

Ticket:
{json.dumps(ticket, indent=2)}

Explain this ticket and its risk level.
"""

        response = ask_model(explain_prompt)

        print("\nMistral:\n")
        print(response.strip())
        print("-" * 60)

        conversation.append(f"Assistant: {response.strip()}")

if __name__ == "__main__":
    main()
