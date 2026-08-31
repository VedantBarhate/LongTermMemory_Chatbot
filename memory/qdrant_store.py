from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
import uuid
from datetime import datetime


class QdrantMemoryStore:
    def __init__(self, collection_name="long_term_memory", vector_size=384):
        self.collection_name = collection_name
        # Local persistent Qdrant database
        self.client = QdrantClient(path="./qdrant_data")
        self._create_collection(vector_size)

    def _create_collection(self, vector_size):
        collections = self.client.get_collections()
        existing_collections = [
            collection.name
            for collection in collections.collections
        ]
        if self.collection_name not in existing_collections:

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )

    def add_memory(self, user_id, memory_text, embedding, memory_type="general", importance=0.5, confidence=1.0, session_id=None):
        memory_id = str(uuid.uuid4())
        payload = {
            "memory_id": memory_id,
            "user_id": user_id,
            "memory": memory_text,
            "memory_type": memory_type,
            "importance": importance,
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "session_id": session_id
        }

        point = PointStruct(
            id=memory_id,
            vector=embedding,
            payload=payload
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        return memory_id

    def search_memories(self, query_embedding, user_id, limit=5):
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(
                            value=user_id
                        )
                    )
                ]
            )

            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                query_filter=query_filter,
                limit=limit
            )

            return results.points