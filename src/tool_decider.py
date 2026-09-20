# AI model picks between CASUAL_CHAT and GENERATE_COMBOS actions based on the current user message and conversation context.
# returns a JSON object with the chosen action and any necessary parameters
import json
from llm_client import ask_model

SYSTEM_PROMPT = """
You are an action decider for a football betting assistant chatbot.

Available Actions/Tools:
- CASUAL_CHAT: Use for casual conversation, greetings, small talk, football definitions, or non-betting responses.
  Examples: "hello", "how are you", "what is BTTS?", "what does expected value mean?", "football is great".
- GENERATE_COMBOS: Use to generate a betting ticket with football predictions or modify an existing one.
  Parameters: "size" (number of selections, e.g., 3 for a 3-leg ticket).
  If not specified, infer from context or default to 3.

You will be given:
1) The user's CURRENT message
2) The conversation so far (optional context)

Tasks:
- Analyze the current message and conversation to decide which action to take.
- For GENERATE_COMBOS, infer the "size" parameter:
    - Use the number in the current message if specified (e.g., "give me a 5-leg ticket" -> size: 5).
    - Use conversation context for relative requests:
        - "add one more" -> previous_size + 1.
        - "make it smaller" -> previous_size - 1.
        - "give me another one" -> maintain previous_size.
    - If no size is specified and no context exists, default to 3.

Rules:
- Choose GENERATE_COMBOS if the user asks for tickets, combos, predictions, "best bets", or wants to modify a previous ticket ("another one", "add one more", "make it safer").
- Choose CASUAL_CHAT for general greetings, football knowledge questions, or acknowledgments ("thanks", "okay")—unless the context strongly implies they are responding to a betting suggestion.
- Do NOT invent betting data. The tool provides the data.
- Output ONLY valid JSON in the specified format.

Examples:
- Current: "Generate a 3-leg ticket" -> {"action": "GENERATE_COMBOS", "params": {"size": 3}}
- Current: "Hello" -> {"action": "CASUAL_CHAT", "params": null}
- Current: "What is BTTS?" -> {"action": "CASUAL_CHAT", "params": null}
- Current: "Add one more game" (previous was 3) -> {"action": "GENERATE_COMBOS", "params": {"size": 4}}
- Current: "Give me another one" (previous was 4) -> {"action": "GENERATE_COMBOS", "params": {"size": 4}}
- Current: "Make this safer" -> {"action": "GENERATE_COMBOS", "params": {"size": null}} // size inferred from context

Format:
{
  "action": "CASUAL_CHAT" | "GENERATE_COMBOS",
  "params": null | {"size": number | null}
}
"""

def decide_action(current_message: str, conversation: str):
    prompt = f"""
{SYSTEM_PROMPT}

Current user message:
{current_message}

Conversation so far (for context if needed):
{conversation}

Answer:
"""
    resp = ask_model(prompt).strip()

    if resp.startswith("```"):
        resp = resp.split("```")[1]
        if resp.startswith("json"):
            resp = resp[4:]
        resp = resp.rstrip("```")

    try:
        data = json.loads(resp)
        return {
            "action": data.get("action", "CASUAL_CHAT"),
            "params": data.get("params")
        }
    except Exception:
        return {
            "action": "CASUAL_CHAT",
            "params": None
        }
