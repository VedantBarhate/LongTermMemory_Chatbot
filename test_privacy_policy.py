from memory.privacy_policy import PrivacyPolicy


def main():

    policy = PrivacyPolicy(mode="ASK")

    candidates = [
        {
            "text": "User's name is Vedant",
            "type": "profile",
            "importance": 0.9,
            "confidence": 1.0
        },
        {
            "text": "User prefers Python over Java",
            "type": "preference",
            "importance": 0.8,
            "confidence": 0.95
        },
        {
            "text": "User's password is abc123",
            "type": "other",
            "importance": 0.9,
            "confidence": 1.0
        },
        {
            "text": "User is interested in computer vision",
            "type": "interest",
            "importance": 0.8,
            "confidence": 0.9
        },
        {
            "text": "User has diabetes",
            "type": "profile",
            "importance": 0.8,
            "confidence": 1.0
        }
    ]

    result = policy.filter_candidates(candidates)

    print("\nAPPROVED MEMORIES")

    for memory in result["approved"]:
        print(f"  + {memory['text']}")

    print("\nREJECTED MEMORIES")

    for item in result["rejected"]:
        print(
            f"  - {item['candidate'].get('text')}"
            f" | Reason: {item['reason']}"
        )


if __name__ == "__main__":
    main()