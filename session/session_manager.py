import uuid
from datetime import datetime


class SessionManager:

    def __init__(self, user_id):
        self.user_id = user_id
        self.current_session_id = None
        self.sessions = {}

        self.create_session()

    def create_session(self):
        session_id = str(uuid.uuid4())[:8]

        self.current_session_id = session_id

        self.sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "messages": []
        }

        return session_id

    def get_current_session(self):
        return self.sessions[self.current_session_id]

    def add_message(self, role, content):
        session = self.get_current_session()

        session["messages"].append({
            "role": role,
            "content": content
        })

    def get_messages(self):
        return self.get_current_session()["messages"]

    def get_session_id(self):
        return self.current_session_id