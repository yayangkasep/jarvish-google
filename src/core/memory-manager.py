from core.database import get_session, User, CoreMemory

class MemoryManager:
    def __init__(self):
        pass

    def _get_or_create_user(self, db, telegram_id):
        telegram_id = str(telegram_id)
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def GetFacts(self, user_id):
        db = get_session()
        try:
            user = self._get_or_create_user(db, user_id)
            memories = db.query(CoreMemory).filter(CoreMemory.user_id == user.id).order_by(CoreMemory.id.asc()).all()
            return [m.fact for m in memories]
        finally:
            db.close()

    def AddFact(self, user_id, fact):
        db = get_session()
        try:
            user = self._get_or_create_user(db, user_id)
            new_memory = CoreMemory(user_id=user.id, fact=fact)
            db.add(new_memory)
            db.commit()
        finally:
            db.close()

    def DeleteFact(self, user_id, fact_index):
        db = get_session()
        try:
            user = self._get_or_create_user(db, user_id)
            memories = db.query(CoreMemory).filter(CoreMemory.user_id == user.id).order_by(CoreMemory.id.asc()).all()
            
            if 0 <= fact_index < len(memories):
                fact_to_delete = memories[fact_index]
                deleted_fact_text = fact_to_delete.fact
                db.delete(fact_to_delete)
                db.commit()
                return deleted_fact_text
            return None
        finally:
            db.close()
