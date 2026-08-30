from llm.openrouter_client import OpenRouterClient


SYSTEM_PROMPT = """
You are a helpful, general-purpose AI assistant.

Answer the user's questions clearly and accurately.
"""


def main():

    llm = OpenRouterClient()

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    print("=" * 50)
    print("       LONG-TERM MEMORY CHATBOT")
    print("             Module 1")
    print("=" * 50)

    print("\nType /exit to quit.\n")

    while True:

        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "/exit":
            print("\nGoodbye!")
            break

        messages.append({
            "role": "user",
            "content": user_input
        })

        try:

            response = llm.generate_response(messages)

            print(f"\nBot: {response}\n")

            messages.append({
                "role": "assistant",
                "content": response
            })

        except Exception as e:

            print(f"\nError communicating with OpenRouter: {e}\n")


if __name__ == "__main__":
    main()