# AI model picks between CASUAL_CHAT and GENERATE_COMBOS actions based on the current user message and conversation context.
# returns a JSON object with the chosen action and any necessary parameters
import json
from llm_client import ask_model

SYSTEM_PROMPT = """
You are an action decider for a football betting assistant chatbot.

Available Actions/Tools:
- CASUAL_CHAT: Use for casual conversation, greetings, small talk, or non-betting responses (e.g., "hello", "how are you", "thanks"). No parameters needed.
- GENERATE_COMBOS: Use to generate a betting ticket with football predictions. Parameters: "size" (number of selections, e.g., 3 for a 3-leg ticket). If not specified, infer from context or default to 3.

You will be given:
1) The user's CURRENT message
2) The conversation so far (optional context)

Tasks:
- Analyze the current message and conversation to decide which action to take.
- For GENERATE_COMBOS, infer the "size" parameter: Use the number in the current message if specified; otherwise, infer/modify from context (e.g., if previous ticket was 3 legs and user says "add one more", set size to 4). If no context, default to 3.
- Do NOT guess numbers without clear context.

Rules:
- Choose GENERATE_COMBOS ONLY if the current message clearly requests betting advice, tickets, combos, or predictions.
- Choose CASUAL_CHAT for greetings, acknowledgments, or casual responses like "hello", "thanks", "great", "okay" — unless the conversation indicates it's a continuation of betting (e.g., "yes" after a ticket suggestion).
- If the current message is ambiguous, use conversation context to decide (e.g., "yes" after betting → GENERATE_COMBOS).
- Output ONLY valid JSON in the specified format.

Examples:
- Current: "Generate a 3-leg ticket" → {"action": "GENERATE_COMBOS", "params": {"size": 3}}
- Current: "Hello" → {"action": "CASUAL_CHAT", "params": null}
- Current: "Thanks" → {"action": "CASUAL_CHAT", "params": null}
- Current: "Give me a ticket" (conversation mentions 4) → {"action": "GENERATE_COMBOS", "params": {"size": 4}}
- Current: "Yes" (after AI suggests a ticket) → {"action": "GENERATE_COMBOS", "params": {"size": null}}  // infer from context
- Current: "Great" (after casual "How are you?") → {"action": "CASUAL_CHAT", "params": null}
- Current: "Add one more game" (after 3-leg ticket) → {"action": "GENERATE_COMBOS", "params": {"size": 4}}

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
