import json
import os
import uuid
from datetime import datetime


class SessionManager:
    def __init__(self, storage_dir="data/sessions"):
        self.storage_dir = storage_dir

        os.makedirs(self.storage_dir, exist_ok=True)

        self.sessions = {}
        self.current_session_id = None

        self._load_sessions()

        # Create a session if none exist
        if not self.sessions:
            self.create_session()

        # Otherwise use the most recently updated session
        else:
            self.current_session_id = max(
                self.sessions,
                key=lambda sid:
                self.sessions[sid]["updated_at"]
            )

    def _load_sessions(self):
        for filename in os.listdir(self.storage_dir):
            if not filename.endswith(".json"):
                continue

            filepath = os.path.join(self.storage_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    session = json.load(file)
                session_id = session["session_id"]
                self.sessions[session_id] = session
            except (json.JSONDecodeError, KeyError):
                print(f"Warning: Could not load {filename}")

    def _save_session(self, session_id):
        session = self.sessions[session_id]
        filepath = os.path.join(self.storage_dir, f"{session_id}.json")

        with open(filepath, "w", encoding="utf-8") as file:

            json.dump(session, file, indent=4, ensure_ascii=False)

    def create_session(self):
        session_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        session = {
            "session_id": session_id,
            "created_at": now,
            "updated_at": now,
            "messages": []
        }

        self.sessions[session_id] = session
        self.current_session_id = session_id
        self._save_session(session_id)

        return session_id

    def switch_session(self, session_id):
        if session_id not in self.sessions:
            return False

        self.current_session_id = session_id
        return True


    def get_current_session(self):
        if self.current_session_id is None:
            return None

        return self.sessions[
            self.current_session_id
        ]

    def add_message(self, role, content):
        session = self.get_current_session()
        if session is None:
            return

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        session["messages"].append(message)
        session["updated_at"] = datetime.now().isoformat()
        self._save_session(self.current_session_id)


    def get_history(self):
        session = self.get_current_session()
        if session is None:
            return []

        return session["messages"]

    def list_sessions(self):
        return list(self.sessions.values())


    def delete_session(self, session_id):
        if session_id not in self.sessions:
            return False

        filepath = os.path.join(self.storage_dir, f"{session_id}.json")

        if os.path.exists(filepath):
            os.remove(filepath)

        del self.sessions[session_id]

        # If deleted session was active,
        # create a new one
        if self.current_session_id == session_id:
            if self.sessions:
                self.current_session_id = max(
                    self.sessions,
                    key=lambda sid:
                    self.sessions[sid]["updated_at"]
                )

            else:

                self.create_session()

        return True