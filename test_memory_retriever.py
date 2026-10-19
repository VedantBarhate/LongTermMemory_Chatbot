
from memory.memory_retriever import MemoryRetriever


def main():
    retriever = MemoryRetriever()
    user_id = "memory_manager_test_user"

    queries = [
        "Which programming language does the user prefer?",
        "What computer science topics interest the user?",
        "What is the user's favorite holiday destination?",
    ]

    for query in queries:
        print(f"\nQuery: {query}")

        memories = retriever.retrieve(query, user_id)

        if not memories:
            print("No relevant memories retrieved.")
            continue

        for memory in memories:
            print(
                f"- {memory['text']} "
                f"(similarity={memory['similarity']:.3f})"
            )


if __name__ == "__main__":
    main()
