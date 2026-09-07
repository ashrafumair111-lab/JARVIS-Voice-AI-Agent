"""Memory tools: save notes (MongoDB + Qdrant) and semantic recall."""

import datetime


class MemoryTools:
    def __init__(self, mongo=None, vectors=None):
        self.mongo = mongo
        self.vectors = vectors

    def save_note(self, text, tags=None):
        text = (text or "").strip()
        if not text:
            return {"error": "Nothing to save."}
        if self.mongo is None or not self.mongo.available:
            return {"error": "MongoDB unavailable - cannot save note."}
        try:
            doc = self.mongo.insert_note(text, tags or [])
            if self.vectors is not None and self.vectors.available:
                try:
                    self.vectors.upsert(
                        [{"text": text, "type": "note",
                          "ts": datetime.datetime.now(
                              datetime.timezone.utc).isoformat()}]
                    )
                except Exception:
                    pass
            return {"saved_note": doc}
        except Exception as exc:
            return {"error": f"Could not save note: {exc}"}

    def recall(self, query, limit=5):
        query = (query or "").strip()
        if not query:
            return {"error": "Empty memory query."}
        if self.vectors is None or not self.vectors.available:
            return {"error": "Qdrant memory unavailable."}
        try:
            hits = self.vectors.search(query, int(limit))
            memory = [
                {
                    "text": h["payload"].get("text", ""),
                    "type": h["payload"].get("type", ""),
                    "score": round(h["score"], 3),
                }
                for h in hits
            ]
            return {"memory": memory}
        except Exception as exc:
            return {"error": f"Memory recall failed: {exc}"}