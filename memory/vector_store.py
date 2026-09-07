"""Qdrant vector memory backed by Cohere embeddings."""

import itertools
import uuid

import config


class VectorStore:
    def __init__(self, cohere_client=None, qdrant_client=None):
        self.available = False
        self.cohere = cohere_client
        self.qdrant = qdrant_client
        try:
            if self.cohere is None and config.COHERE_API_KEY:
                import cohere

                self.cohere = cohere.Client(config.COHERE_API_KEY)
            if self.qdrant is None and config.QDRANT_URL:
                from qdrant_client import QdrantClient

                self.qdrant = QdrantClient(
                    url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY
                )
            if self.cohere is not None and self.qdrant is not None:
                self._ensure_collection()
                self.available = True
        except Exception as exc:
            print(f"[QDRANT] unavailable: {exc}")

    def _ensure_collection(self):
        try:
            self.qdrant.get_collection(config.MEMORY_COLLECTION)
        except Exception:
            from qdrant_client.models import Distance, VectorParams

            self.qdrant.create_collection(
                collection_name=config.MEMORY_COLLECTION,
                vectors_config=VectorParams(
                    size=config.VECTOR_SIZE, distance=Distance.COSINE
                ),
            )

    def _embed(self, texts, input_type):
        resp = self.cohere.embed(
            texts=texts, model=config.EMBED_MODEL, input_type=input_type
        )
        return resp.embeddings

    def upsert(self, items):
        """items: list of dicts {text, type, ts?}"""
        if not self.available:
            return 0
        from qdrant_client.models import PointStruct

        texts = [it["text"] for it in items]
        vectors = self._embed(texts, "search_document")
        points = []
        for it, vec in zip(items, vectors):
            pid = it.get("id") or str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=pid,
                    vector=vec,
                    payload={
                        "text": it["text"],
                        "type": it.get("type", "note"),
                        "ts": it.get("ts", ""),
                    },
                )
            )
        self.qdrant.upsert(
            collection_name=config.MEMORY_COLLECTION, points=points
        )
        return len(points)

    def search(self, query, limit=5):
        if not self.available:
            return []
        vec = self._embed([query], "search_query")[0]
        res = self.qdrant.search(
            collection_name=config.MEMORY_COLLECTION,
            query_vector=vec,
            limit=limit,
            score_threshold=0.55,
        )
        return [
            {"id": h.id, "score": h.score, "payload": h.payload} for h in res
        ]