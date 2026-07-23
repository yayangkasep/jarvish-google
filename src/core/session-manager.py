import json
from core.database import get_session, User, ChatHistory, init_db

class SessionManager:
    def __init__(self):
        # Ensure database tables exist
        init_db()
        # Limit active context window to 20 messages to save LLM tokens
        self.MAX_HISTORY = 20

    def _get_or_create_user(self, db, telegram_id):
        telegram_id = str(telegram_id)
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def GetHistory(self, user_id):
        db = get_session()
        try:
            user = self._get_or_create_user(db, user_id)
            # Only get active chats for context window
            chats = db.query(ChatHistory).filter(
                ChatHistory.user_id == user.id,
                ChatHistory.active == 1
            ).order_by(ChatHistory.timestamp.desc()).limit(self.MAX_HISTORY).all()
            
            # Reverse to maintain chronological order for LLM
            chats.reverse()
            
            history = []
            for chat in chats:
                try:
                    msg = json.loads(chat.message_json)
                    history.append(msg)
                except Exception as e:
                    print(f"Failed to parse chat json: {e}")
            return history
        finally:
            db.close()

    def AddMessage(self, user_id, role, content, **kwargs):
        db = get_session()
        try:
            user = self._get_or_create_user(db, user_id)
            
            msg = {"role": role, "content": content}
            msg.update(kwargs)
            
            new_chat = ChatHistory(
                user_id=user.id,
                message_json=json.dumps(msg)
            )
            db.add(new_chat)
            db.commit()
        finally:
            db.close()

    def ClearSession(self, user_id):
        db = get_session()
        try:
            user = self._get_or_create_user(db, user_id)
            # Archive chats instead of deleting to preserve long-term history
            db.query(ChatHistory).filter(
                ChatHistory.user_id == user.id,
                ChatHistory.active == 1
            ).update({"active": 0})
            db.commit()
        finally:
            db.close()

    def CleanupIncompleteTurns(self, user_id):
        # Incomplete turns cleanup can be skipped for now, 
        # or we just remove the last message if it's a tool call.
        db = get_session()
        try:
            user = self._get_or_create_user(db, user_id)
            last_chat = db.query(ChatHistory).filter(
                ChatHistory.user_id == user.id,
                ChatHistory.active == 1
            ).order_by(ChatHistory.timestamp.desc()).first()
            
            if not last_chat:
                return
                
            msg = json.loads(last_chat.message_json)
            role = msg.get("role")
            
            # If the last message in DB is a tool call or assistant tool invocation, delete it
            # This ensures we don't have dangling tool calls if it crashes
            if role == "tool" or (role == "assistant" and msg.get("tool_calls")):
                db.delete(last_chat)
                db.commit()
                # Run recursively in case there are multiple
                self.CleanupIncompleteTurns(user_id)
        except Exception as e:
            print(f"Cleanup error: {e}")
        finally:
            db.close()
