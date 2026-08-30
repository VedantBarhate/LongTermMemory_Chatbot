from sentence_transformers import SentenceTransformer


class EmbeddingModel:

    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, text):
        """
        Convert a single text string into an embedding vector.
        """
        return self.model.encode(
            text,
            convert_to_numpy=True
        ).tolist()

    def encode_batch(self, texts):
        """
        Convert multiple texts into embedding vectors.
        """
        return self.model.encode(
            texts,
            convert_to_numpy=True
        ).tolist()

    def get_dimension(self):
        """
        Return the dimensionality of the embeddings.
        """
        return self.model.get_sentence_embedding_dimension()