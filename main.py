from llm.openrouter_client import OpenRouterClient
from session.session_manager import SessionManager


SYSTEM_PROMPT = """
You are a helpful, general-purpose AI assistant.

Answer the user's questions clearly and accurately.
"""


def main():

    llm = OpenRouterClient()

    # For now, we use a fixed user ID.
    # Later this will come from authentication/user management.
    user_id = "user_001"

    session_manager = SessionManager(user_id)

    print("=" * 50)
    print("       LONG-TERM MEMORY CHATBOT")
    print("=" * 50)

    print(f"\nUser ID: {user_id}")
    print(f"Session ID: {session_manager.get_session_id()}")

    print("\nType /newsession to start a new session.")
    print("Type /exit to quit.\n")

    while True:

        user_input = input("You: ").strip()

        if not user_input:
            continue

        # Exit
        if user_input.lower() == "/exit":
            print("\nGoodbye!")
            break

        # Create a new session
        if user_input.lower() == "/newsession":

            session_id = session_manager.create_session()

            print(f"\n✓ New session created.")
            print(f"Session ID: {session_id}\n")

            continue

        # Store user message
        session_manager.add_message(
            role="user",
            content=user_input
        )

        # Build messages for LLM
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        messages.extend(
            session_manager.get_messages()
        )

        try:

            response = llm.generate_response(messages)

            print(f"\nBot: {response}\n")

            # Store assistant response
            session_manager.add_message(
                role="assistant",
                content=response
            )

        except Exception as e:

            print(
                f"\nError communicating with OpenRouter: {e}\n"
            )


if __name__ == "__main__":
    main()