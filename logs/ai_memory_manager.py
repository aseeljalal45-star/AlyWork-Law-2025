import json
import os
from datetime import datetime

class AIMemoryManager:
    def __init__(self, path="helpers/ai_memory.json"):
        self.path = path
        self.memory = self.load_memory()

    def load_memory(self):
        """تحميل الذاكرة من JSON أو إنشاء بنية جديدة"""
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f).get("memory", [])
            except json.JSONDecodeError:
                print("⚠️ خطأ في ملف ai_memory.json، سيتم إنشاء بنية فارغة")
                return []
        else:
            return []

    def save_memory(self):
        """حفظ الذاكرة إلى JSON"""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"memory": self.memory}, f, ensure_ascii=False, indent=4)

    def add_interaction(self, role, query, response, reference="", example="", notes="", context_tags=None):
        """إضافة تفاعل جديد"""
        if context_tags is None:
            context_tags = []
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "role": role,
            "query": query,
            "response": response,
            "reference": reference,
            "example": example,
            "notes": notes,
            "context_tags": context_tags
        }
        self.memory.append(new_entry)
        self.save_memory()
        return new_entry

    def search_memory(self, keyword, role=None):
        """البحث في الذاكرة باستخدام كلمة مفتاحية وخيار تحديد الدور"""
        results = []
        for entry in self.memory:
            if (keyword.lower() in entry["query"].lower() or keyword.lower() in entry["response"].lower()):
                if role is None or entry["role"] == role:
                    results.append(entry)
        return results

    def update_interaction(self, index, **kwargs):
        """تعديل تفاعل موجود بالاعتماد على index"""
        if 0 <= index < len(self.memory):
            for key, value in kwargs.items():
                if key in self.memory[index]:
                    self.memory[index][key] = value
            self.save_memory()
            return self.memory[index]
        else:
            raise IndexError("❌ فهرس غير صالح للتعديل")

    def clear_memory(self):
        """مسح كل الذاكرة"""
        self.memory = []
        self.save_memory()