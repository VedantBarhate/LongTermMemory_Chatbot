from memory.memory_extractor import MemoryExtractor


def main():
    extractor = MemoryExtractor()

    test_messages = [
        "My name is Vedant.",
        "I am a CSE student interested in computer vision.",
        "What's the weather today?",
        "I prefer Python over Java.",
        "Thanks, that was helpful.",
        "I am hungry right now.",
        "I'm currently working on an image captioning project."
    ]

    for message in test_messages:
        print("\n" + "=" * 60)
        print(f"USER: {message}")
        result = extractor.extract(message)
        print("\nEXTRACTOR RESULT:")
        print(result)

if __name__ == "__main__":
    main()