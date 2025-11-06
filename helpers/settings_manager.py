import json
import os
import streamlit as st
from datetime import datetime

class SettingsManager:
    def __init__(self, path="helpers/settings.json"):
        self.path = path
        self.settings = self.load_settings()

    # ==============================
    # تحميل الإعدادات من ملف JSON أو إعدادات افتراضية
    # ==============================
    def load_settings(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                st.info(f"✅ تم تحميل الإعدادات بنجاح ({len(settings)} إعداد).")
                return settings
            except json.JSONDecodeError as e:
                st.warning(f"⚠️ خطأ في ملف الإعدادات: {e}. سيتم استخدام الإعدادات الافتراضية.")
                return self.default_settings()
        else:
            st.warning("⚠️ لم يتم العثور على ملف settings.json، سيتم إنشاء إعدادات افتراضية.")
            return self.default_settings()

    # ==============================
    # إعدادات افتراضية
    # ==============================
    def default_settings(self):
        return {
            "APP_NAME": "AlyWork Law Pro",
            "SHEET_URL": "",
            "LANG": "ar",
            "THEME": "فاتح",
            "VERSION": "v25.0",
            "LAST_UPDATED": datetime.now().isoformat()
        }

    # ==============================
    # حفظ الإعدادات مع تسجيل الوقت
    # ==============================
    def save_settings(self):
        self.settings["LAST_UPDATED"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
            st.success("✅ تم حفظ الإعدادات بنجاح.")
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء حفظ الإعدادات: {e}")

    # ==============================
    # الحصول على قيمة إعداد
    # ==============================
    def get(self, key, default=None):
        return self.settings.get(key, default)

    # ==============================
    # تعيين قيمة إعداد جديدة وحفظها تلقائيًا
    # ==============================
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    # ==============================
    # تحديث إعدادات متعددة دفعة واحدة
    # ==============================
    def update(self, new_settings: dict):
        if isinstance(new_settings, dict):
            self.settings.update(new_settings)
            self.save_settings()
        else:
            st.error("⚠️ يجب أن يكون التحديث على شكل dict.")

    # ==============================
    # إعادة الإعدادات إلى الافتراضية
    # ==============================
    def reset_to_default(self):
        self.settings = self.default_settings()
        self.save_settings()
        st.info("♻️ تم إعادة الإعدادات إلى الوضع الافتراضي.")