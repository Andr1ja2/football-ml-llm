import json
from llm_client import ask_model

SYSTEM_PROMPT = """
You are an intent classifier.

Classify the user message into ONE intent:

- BETTING_REQUEST
- MATCH_QUERY
- CASUAL_CHAT

Rules:
- BETTING_REQUEST: user asks for bets, tickets, combos, predictions, safest option.
- MATCH_QUERY: user mentions a specific match but does NOT explicitly ask for a bet.
- CASUAL_CHAT: greetings or general conversation.

Output ONLY valid JSON:
{
  "intent": "BETTING_REQUEST | MATCH_QUERY | CASUAL_CHAT"
}
"""

def decide_intent(user_input):
    prompt = f"""
{SYSTEM_PROMPT}

User message:
{user_input}

Classification:
"""
    resp = ask_model(prompt).strip()

    if resp.startswith("```"):
        resp = resp.split("```")[1]

    try:
        return json.loads(resp)["intent"]
    except Exception:
        return "CASUAL_CHAT"
