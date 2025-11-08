import json
import os
import streamlit as st
from datetime import datetime

class SettingsManager:
    def __init__(self, path="helpers/config.json"):
        self.path = path
        self.settings = self.load_settings()
        st.session_state["config"] = self.settings

    def load_settings(self):
        """تحميل الإعدادات"""
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return self.default_settings()
        return self.default_settings()

    def default_settings(self):
        """الإعدادات الافتراضية"""
        return {
            "APP_INFO": {
                "APP_NAME": "⚖️ منصة قانون العمل الذكية",
                "VERSION": "v25.1",
                "SUPPORT_EMAIL": "support@alyworklaw.com"
            },
            "DATA_SOURCES": {
                "WORKBOOK_PATH": "data/AlyWork_Law_Pro_v2025_v24_ColabStreamlitReady.xlsx",
                "SHEET_URL": ""
            },
            "AI_FEATURES": {
                "ENABLE_AI": True,
                "MAX_HISTORY": 20
            },
            "FOOTER": {
                "TEXT": "© 2025 منصة قانون العمل الذكية — جميع الحقوق محفوظة."
            }
        }

    def update(self, new_settings):
        """تحديث الإعدادات"""
        for key, value in new_settings.items():
            if isinstance(value, dict) and key in self.settings:
                self.settings[key].update(value)
            else:
                self.settings[key] = value
        self.save_settings()

    def save_settings(self):
        """حفظ الإعدادات"""
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            st.error(f"❌ خطأ في حفظ الإعدادات: {e}")