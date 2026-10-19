from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    FilterSelector
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

    def update_memory(self, memory_id, memory_text, embedding,
                      importance=None, confidence=None, memory_type=None,
                      session_id=None):
        """Update an existing memory while preserving its ID."""
        points = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[memory_id],
            with_payload=True,
            with_vectors=False
        )

        if not points:
            return False

        payload = dict(points[0].payload or {})
        payload["memory"] = memory_text
        payload["updated_at"] = datetime.now().isoformat()

        if importance is not None:
            payload["importance"] = importance
        if confidence is not None:
            payload["confidence"] = confidence
        if memory_type is not None:
            payload["memory_type"] = memory_type
        if session_id is not None:
            payload["session_id"] = session_id

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=memory_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )
        return True

    def list_memories(self, user_id, limit=100):
        """List stored memories belonging to one user."""
        results, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
            with_vectors=False
        )
        return results

    def delete_memory(self, memory_id, user_id):
        """Delete a memory only if it belongs to the specified user."""
        points = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[memory_id],
            with_payload=True,
            with_vectors=False
        )

        if not points or points[0].payload.get("user_id") != user_id:
            return False

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[memory_id]
        )
        return True

    
    def delete_all_memories(self, user_id):
        """Delete all long-term memories belonging to one user."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id),
                        )
                    ]
                )
            ),
        )
