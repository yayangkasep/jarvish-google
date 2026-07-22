import os
import json


class SessionManager:
    def __init__(self, data_file="data/sessions.json"):
        self.data_file = os.path.join(os.path.dirname(__file__), "..", data_file)
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        self.sessions = self.LoadSessions()
        # Ensure max 20 messages per session to avoid blowing up context window
        self.MAX_HISTORY = 20

    def LoadSessions(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading sessions: {e}")
        return {}

    def SaveSessions(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")

    def GetHistory(self, user_id):
        user_id = str(user_id)
        if user_id not in self.sessions:
            self.sessions[user_id] = []

        return self.sessions[user_id]

    def AddMessage(self, user_id, role, content, **kwargs):
        user_id = str(user_id)
        if user_id not in self.sessions:
            self.sessions[user_id] = []

        msg = {"role": role, "content": content}
        msg.update(kwargs)
        self.sessions[user_id].append(msg)

        # Trim history if too long
        if len(self.sessions[user_id]) > self.MAX_HISTORY:
            # Keep the last MAX_HISTORY messages
            self.sessions[user_id] = self.sessions[user_id][-self.MAX_HISTORY :]

        self.SaveSessions()

    def ClearSession(self, user_id):
        user_id = str(user_id)
        if user_id in self.sessions:
            self.sessions[user_id] = []
            self.SaveSessions()
