
from memory.memory_manager import MemoryManager
from memory.privacy_policy import PrivacyPolicy


def main():
    manager = MemoryManager(
        privacy_policy=PrivacyPolicy(mode="AUTO")
    )

    # Use a stable test ID so these memories can be found on later runs.
    user_id = "memory_manager_test_user"

    candidates = [
        {
            "text": "User prefers Python over Java",
            "type": "preference",
            "importance": 0.8,
            "confidence": 0.95,
        },
        {
            "text": "User is interested in computer vision",
            "type": "interest",
            "importance": 0.8,
            "confidence": 0.9,
        },
        {
            "text": "User's password is example-secret-123",
            "type": "other",
            "importance": 0.9,
            "confidence": 1.0,
        },
    ]

    report = manager.process_candidates(
        candidates=candidates,
        user_id=user_id,
        session_id="test-session"
    )

    print("\nProcessing report:")
    for category, items in report.items():
        print(f"\n{category.upper()} ({len(items)}):")
        for item in items:
            print(item)

    print("\nStored memories:")
    for point in manager.get_memories(user_id):
        print({
            "id": str(point.id),
            "memory": point.payload.get("memory"),
            "type": point.payload.get("memory_type"),
        })


if __name__ == "__main__":
    main()
