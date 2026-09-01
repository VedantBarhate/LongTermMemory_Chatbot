from llm.openrouter_client import OpenRouterClient
from session.session_manager import SessionManager

def print_sessions(session_manager):
    sessions = session_manager.list_sessions()
    print("\nAvailable sessions:")
    for session in sessions:
        session_id = session["session_id"]
        message_count = len(session["messages"])
        current = (" ← current" if session_id == session_manager.current_session_id else "")
        print(
            f"  {session_id} | "
            f"{message_count} messages"
            f"{current}"
        )

def print_history(session_manager):
    history = session_manager.get_history()
    if not history:
        print("\nNo messages in this session.")
        return
    print("\n--- Conversation History ---")

    for message in history:
        role = message["role"].upper()
        print(
            f"\n{role}: "
            f"{message['content']}"
        )


SYSTEM_PROMPT = """
You are a helpful, general-purpose AI assistant.

Answer the user's questions clearly and accurately.
"""


def main():
    session_manager = SessionManager()
    llm = OpenRouterClient()

    print("\n================================")
    print("       Long-Term Memory Chatbot")
    print("================================")

    print(
        f"\nCurrent session: "
        f"{session_manager.current_session_id}"
    )

    print(
        "\nCommands:"
        "\n  /new"
        "\n  /sessions"
        "\n  /use <session_id>"
        "\n  /current"
        "\n  /history"
        "\n  /delete <session_id>"
        "\n  /exit"
    )

    while True:
        try:
            user_input = input(
                "\nYou: "
            ).strip()

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if not user_input:
            continue

        if user_input == "/exit":

            break

        elif user_input == "/new":
            session_id = (
                session_manager.create_session()
            )

            print(
                f"\nNew session created: "
                f"{session_id}"
            )
            continue


        elif user_input == "/sessions":
            print_sessions(session_manager)
            continue

        elif user_input.startswith("/use "):
            session_id = user_input[
                len("/use "):
            ].strip()
            if session_manager.switch_session(session_id):
                print(
                    f"\nSwitched to session "
                    f"{session_id}"
                )
            else:
                print(
                    f"\nSession '{session_id}' "
                    f"does not exist."
                )
            continue

        elif user_input == "/current":
            print(
                f"\nCurrent session: "
                f"{session_manager.current_session_id}"
            )
            continue

        elif user_input == "/history":
            print_history(
                session_manager
            )
            continue

        elif user_input.startswith("/delete "):
            session_id = user_input[
                len("/delete "):
            ].strip()
            if session_manager.delete_session(session_id):
                print(
                    f"\nDeleted session "
                    f"{session_id}"
                )
                print(
                    f"Current session: "
                    f"{session_manager.current_session_id}"
                )
            else:
                print(
                    f"\nSession '{session_id}' "
                    f"does not exist."
                )
            continue

        # NORMAL ONES
        session_manager.add_message(
            "user",
            user_input
        )

        history = session_manager.get_history()

        llm_messages = [
            {
                "role": message["role"],
                "content": message["content"]
            }
            for message in history
        ]

        response = llm.generate_response(llm_messages)
        print(f"\nAssistant: {response}")
        session_manager.add_message("assistant", response)

    print("\nGoodbye!")

if __name__ == "__main__":
    main()