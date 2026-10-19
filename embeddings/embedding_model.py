import time
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(
        self,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        local_files_only=False,
    ):
        self.model_name = model_name

        start = time.perf_counter()

        print(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(
            model_name,
            local_files_only=local_files_only,
        )

        elapsed = time.perf_counter() - start
        print(f"Model loaded in {elapsed:.2f} seconds.")

    def encode(self, text):
        return self.model.encode(
            text,
            convert_to_numpy=True,
        ).tolist()

    def encode_batch(self, texts):
        return self.model.encode(
            texts,
            convert_to_numpy=True,
        ).tolist()

    def get_dimension(self):
        return self.model.get_sentence_embedding_dimension()
