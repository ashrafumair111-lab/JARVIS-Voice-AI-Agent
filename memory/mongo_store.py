"""MongoDB persistence: transcripts, notes, command audit log."""

import datetime

import config
import pymongo


class MongoStore:
    def __init__(self, url=None, db_name=None):
        self.available = False
        self.client = None
        self.db = None
        try:
            self.client = pymongo.MongoClient(
                url or config.MONGO_URL, serverSelectionTimeoutMS=8000
            )
            self.client.admin.command("ping")
            self.db = self.client[db_name or config.MONGO_DB]
            self.available = True
        except Exception as exc:
            print(f"[MONGO] unavailable: {exc}")

    @staticmethod
    def _now():
        return datetime.datetime.now(datetime.timezone.utc)

    def save_message(self, session_id, role, content):
        if not self.available:
            return None
        return self.db.messages.insert_one(
            {"session": session_id, "role": role, "content": content,
             "ts": self._now()}
        ).inserted_id

    def insert_note(self, text, tags=None):
        if not self.available:
            raise RuntimeError("MongoDB unavailable")
        doc = {"text": text, "tags": tags or [], "ts": self._now()}
        result = self.db.notes.insert_one(doc)
        return {"id": str(result.inserted_id), "text": text, "tags": tags or []}

    def log_command(self, command, status, detail=""):
        if not self.available:
            return
        try:
            self.db.command_log.insert_one(
                {"command": command, "status": status, "detail": detail,
                 "ts": self._now()}
            )
        except Exception:
            pass

    def list_recent_notes(self, limit=10):
        if not self.available:
            return []
        return list(
            self.db.notes.find({}, {"_id": 0, "text": 1, "ts": 1})
                       .sort("ts", -1).limit(limit)
        )