import os
import json
from config import paths


class MemoryManager:
    def __init__(self, data_file="memories.json"):
        self.data_file = os.path.join(paths.get_data_dir(), data_file)
        self.memories = self.LoadMemories()

    def LoadMemories(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memories: {e}")
        return {}

    def SaveMemories(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.memories, f, indent=2)
        except Exception as e:
            print(f"Error saving memories: {e}")

    def GetFacts(self, user_id):
        user_id = str(user_id)
        if user_id not in self.memories:
            self.memories[user_id] = []
        return self.memories[user_id]

    def AddFact(self, user_id, fact):
        user_id = str(user_id)
        if user_id not in self.memories:
            self.memories[user_id] = []
        self.memories[user_id].append(fact)
        self.SaveMemories()
        return True

    def DeleteFact(self, user_id, fact_index):
        user_id = str(user_id)
        if user_id in self.memories:
            try:
                idx = int(fact_index)
                if 0 <= idx < len(self.memories[user_id]):
                    deleted = self.memories[user_id].pop(idx)
                    self.SaveMemories()
                    return deleted
            except Exception:
                pass
        return None
