from embeddings.embedding_model import EmbeddingModel
from sentence_transformers.util import cos_sim


def main():

    embedding_model = EmbeddingModel()

    texts = [
        "I like computer vision",
        "I am interested in image processing",
        "The weather is very nice today"
    ]

    embeddings = embedding_model.encode_batch(texts)

    similarity_1 = cos_sim(
        embeddings[0],
        embeddings[1]
    )

    similarity_2 = cos_sim(
        embeddings[0],
        embeddings[2]
    )

    print(
        "Similarity between:\n"
        f"'{texts[0]}'\n"
        f"'{texts[1]}'"
    )

    print(similarity_1)

    print(
        "\nSimilarity between:\n"
        f"'{texts[0]}'\n"
        f"'{texts[2]}'"
    )

    print(similarity_2)


if __name__ == "__main__":
    main()