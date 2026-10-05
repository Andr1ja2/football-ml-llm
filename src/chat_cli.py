# This script implements a command-line interface for a tool-aware betting chat application.
# It allows users to interact with an AI model that can either engage in casual conversation or generate football betting tickets based on user input.
# The AI model decides the appropriate action based on the user's message and the conversation context.
# The LLM's role is to understand the user's request and decide which tool to invoke, present the results and avoid making up information.
import json
from chat_manager import ChatManager

def main():
    print("=== Tool-Aware Betting Chat ===")
    print("Type 'exit' to quit.\n")

    chat_manager = ChatManager()

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        response, ticket = chat_manager.process_message(user_input)
        response = response.replace("\\n", "\n")

        print("\nAgent:\n")
        print(response)
        print("-" * 60)

if __name__ == "__main__":
    main()
