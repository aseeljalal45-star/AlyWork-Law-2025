import json
import os
import streamlit as st
from datetime import datetime

class SettingsManager:
    def __init__(self, path="helpers/config.json"):
        self.path = path
        self.settings = self.load_settings()
        st.session_state["config"] = self.settings  # تحميل مباشر إلى session state

    def load_settings(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                return settings
            except json.JSONDecodeError as e:
                st.warning(f"⚠️ خطأ في ملف الإعدادات: {e}. سيتم استخدام الإعدادات الافتراضية.")
                return self.default_settings()
        else:
            st.warning("⚠️ لم يتم العثور على ملف config.json، سيتم إنشاء إعدادات افتراضية.")
            return self.default_settings()

    def default_settings(self):
        return {
            "APP_NAME": "AlyWork Law Pro",
            "VERSION": "v25.0",
            "LANG": "ar",
            "THEME": "فاتح",
            "WORKBOOK_PATH": "AlyWork_Law_Pro_v2025_v24_ColabStreamlitReady.xlsx",
            "SHEET_URL": "",
            "CACHE": {"ENABLED": True, "TTL_SECONDS": 600},
            "UI": {"STYLES_LIGHT": "assets/styles_light.css", "STYLES_DARK": "assets/styles_dark.css", "ICON_PATH": "assets/icons/"},
            "AI": {"ENABLE": True, "MEMORY_PATH": "ai_memory.json", "LOGS_PATH": "AI_Analysis_Logs.csv", "MAX_HISTORY": 20},
            "RECOMMENDER": {"MAX_CARDS": 6, "ROLES": ["العمال", "اصحاب العمل", "مفتشو العمل", "الباحثون والمتدربون"]},
            "SIDEBAR": {"MENU_ITEMS": []},
            "FOOTER": {"TEXT": "© 2025 AlyWork Law Pro — جميع الحقوق محفوظة."}
        }

    def save_settings(self):
        self.settings["LAST_UPDATED"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
            st.session_state["config"] = self.settings
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء حفظ الإعدادات: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def update(self, new_settings: dict):
        if isinstance(new_settings, dict):
            self.settings.update(new_settings)
            self.save_settings()
        else:
            st.error("⚠️ يجب أن يكون التحديث على شكل dict.")

    def reset_to_default(self):
        self.settings = self.default_settings()
        self.save_settings()