
from memory.qdrant_store import QdrantMemoryStore
from memory.privacy_policy import PrivacyPolicy
from embeddings.embedding_model import EmbeddingModel


class MemoryManager:
    # Cosine similarity thresholds; tune these using evaluation data.
    DUPLICATE_THRESHOLD = 0.92
    REVIEW_THRESHOLD = 0.78

    def __init__(self, store=None, embedder=None, privacy_policy=None):
        self.store = store or QdrantMemoryStore()
        self.embedder = embedder or EmbeddingModel()
        self.privacy_policy = privacy_policy or PrivacyPolicy(mode="AUTO")

    def process_candidates(self, candidates, user_id, session_id=None):
        """
        Process extracted memory candidates.

        Returns a report of created, updated, rejected, and
        review-needed candidates.
        """
        report = {
            "created": [],
            "updated": [],
            "rejected": [],
            "needs_review": [],
        }

        # Privacy screening must happen before vector storage.
        policy_result = self.privacy_policy.filter_candidates(candidates)

        report["rejected"].extend(policy_result["rejected"])

        for candidate in policy_result["approved"]:
            text = candidate["text"].strip()
            memory_type = candidate["type"]
            importance = float(candidate["importance"])
            confidence = float(candidate["confidence"])

            embedding = self.embedder.encode(text)

            matches = self.store.search_memories(
                query_embedding=embedding,
                user_id=user_id,
                limit=5
            )

            # Only compare memories of the same type. A profile fact
            # and a project fact should not automatically replace each other.
            same_type = [
                point for point in matches
                if (point.payload or {}).get("memory_type") == memory_type
            ]

            best_match = same_type[0] if same_type else None
            score = (
                float(best_match.score)
                if best_match is not None
                and best_match.score is not None
                else -1.0
            )

            if best_match is not None and score >= self.DUPLICATE_THRESHOLD:
                # Update the existing record instead of creating another.
                updated = self.store.update_memory(
                    memory_id=str(best_match.id),
                    memory_text=text,
                    embedding=embedding,
                    importance=importance,
                    confidence=confidence,
                    memory_type=memory_type,
                    session_id=session_id,
                )

                if updated:
                    report["updated"].append({
                        "memory_id": str(best_match.id),
                        "text": text,
                        "similarity": score,
                    })
                else:
                    report["needs_review"].append({
                        "text": text,
                        "reason": "Similar memory was found but could not be updated.",
                    })

            elif best_match is not None and score >= self.REVIEW_THRESHOLD:
                # Similarity alone cannot reliably distinguish a
                # paraphrase from a contradiction. Do not overwrite it.
                report["needs_review"].append({
                    "text": text,
                    "existing_memory": (best_match.payload or {}).get("memory"),
                    "existing_memory_id": str(best_match.id),
                    "similarity": score,
                    "reason": "Potential duplicate or conflicting information.",
                })

            else:
                memory_id = self.store.add_memory(
                    user_id=user_id,
                    memory_text=text,
                    embedding=embedding,
                    memory_type=memory_type,
                    importance=importance,
                    confidence=confidence,
                    session_id=session_id,
                )

                report["created"].append({
                    "memory_id": memory_id,
                    "text": text,
                })

        return report

    def get_memories(self, user_id, limit=100):
        """Return stored memories for the specified user."""
        return self.store.list_memories(user_id=user_id, limit=limit)

    def forget_memory(self, user_id, memory_id):
        """Delete a single memory belonging to the specified user."""
        return self.store.delete_memory(
            memory_id=memory_id,
            user_id=user_id
        )
