import json
import os

class ConfigManager:
    def __init__(self, path="helpers/config.json"):
        self.path = path
        self.config = self.load_config()

    def load_config(self):
        """تحميل ملف config.json أو إنشاء إعدادات افتراضية إذا لم يكن موجودًا"""
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                print(f"⚠️ خطأ في ملف config.json: {e}")
                return self.default_config()
        else:
            print("⚠️ لم يتم العثور على ملف config.json، سيتم إنشاء ملف افتراضي.")
            self.save_config(self.default_config())
            return self.default_config()

    def default_config(self):
        """إعدادات افتراضية"""
        return {
            "APP_NAME": "AlyWork Law Pro",
            "VERSION": "v25.0",
            "LANG": "ar",
            "THEME": "فاتح",
            "WORKBOOK_PATH": "AlyWork_Law_Pro_v2025_v24_ColabStreamlitReady.xlsx",
            "SHEET_URL": "",
            "CACHE": {"ENABLED": True, "TTL_SECONDS": 600},
            "UI": {"STYLES_LIGHT": "assets/styles_light.css", "STYLES_DARK": "assets/styles_dark.css", "ICON_PATH": "assets/icons/"},
            "AI": {"ENABLE": True, "MEMORY_PATH": "ai_memory.json", "LOGS_PATH": "AI_Analysis_Logs.csv"},
            "RECOMMENDER": {"MAX_CARDS": 6},
            "SIDEBAR": {"MENU_ITEMS": []},
            "FOOTER": {"TEXT": "© 2025 AlyWork Law Pro — جميع الحقوق محفوظة."}
        }

    def save_config(self, config=None):
        """حفظ الإعدادات الحالية أو config معين"""
        cfg = config or self.config
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)

    def get(self, key, default=None):
        """الحصول على قيمة من config"""
        return self.config.get(key, default)

    def set(self, key, value):
        """تعديل قيمة في config وحفظها"""
        self.config[key] = value
        self.save_config()

    def get_nested(self, *keys, default=None):
        """الوصول للقيم المتداخلة بسهولة"""
        cfg = self.config
        for key in keys:
            cfg = cfg.get(key, {})
        return cfg or default