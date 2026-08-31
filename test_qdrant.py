from embeddings.embedding_model import EmbeddingModel
from memory.qdrant_store import QdrantMemoryStore


def main():

    embedding_model = EmbeddingModel()

    qdrant = QdrantMemoryStore(
        collection_name="test_memory"
    )

    user_id = "user_001"

    memories = [
        (
            "I am a CSE student",
            "profile",
            0.8
        ),
        (
            "I am interested in computer vision",
            "interest",
            0.9
        ),
        (
            "I prefer Python for programming",
            "preference",
            0.7
        ),
        (
            "I enjoy playing football",
            "hobby",
            0.5
        )
    ]

    # Insert memories
    for memory_text, memory_type, importance in memories:

        embedding = embedding_model.encode(
            memory_text
        )

        memory_id = qdrant.add_memory(
            user_id=user_id,
            memory_text=memory_text,
            embedding=embedding,
            memory_type=memory_type,
            importance=importance
        )

        print(
            f"Stored: {memory_text}"
        )
        print(
            f"ID: {memory_id}\n"
        )

    # Search
    query = "What are my technical interests?"

    query_embedding = embedding_model.encode(
        query
    )

    results = qdrant.search_memories(
        query_embedding=query_embedding,
        user_id=user_id,
        limit=3
    )

    print("\nSearch query:")
    print(query)

    print("\nRetrieved memories:")

    for result in results:

        print(
            f"\nScore: {result.score:.4f}"
        )

        print(
            f"Memory: "
            f"{result.payload['memory']}"
        )


if __name__ == "__main__":
    main()