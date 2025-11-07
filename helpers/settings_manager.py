import json
import os
import streamlit as st
from datetime import datetime
import pandas as pd
from typing import Any, Dict, Optional

class SettingsManager:
    def __init__(self, path: str = "helpers/config.json"):
        """
        🎛️ مدير الإعدادات المتقدم - الإصدار المحسن
        
        يدير إعدادات التطبيق مع ميزات متقدمة للأمان والمرونة
        """
        self.path = path
        self.settings = self.load_settings()
        self.backup_path = f"{path}.backup"
        
        # تحميل مباشر إلى session state للتطبيق السريع
        st.session_state["config"] = self.settings
        
        # تسجيل عملية التهيئة
        self._log_event("system_initialized", f"تم تهيئة مدير الإعدادات من {path}")

    def load_settings(self) -> Dict[str, Any]:
        """
        تحميل الإعدادات من الملف مع معالجة متقدمة للأخطاء
        """
        # محاولة تحميل الإعدادات الحالية
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                
                # التحقق من صحة الهيكل الأساسي
                if self._validate_settings(settings):
                    st.success("✅ تم تحميل الإعدادات بنجاح")
                    self._log_event("settings_loaded", f"تم تحميل {len(settings)} إعداد")
                    return settings
                else:
                    st.warning("⚠️ إعدادات غير صالحة، سيتم استخدام الإعدادات الافتراضية")
                    return self._create_default_settings()
                    
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                st.error(f"❌ خطأ في تنسيق ملف الإعدادات: {e}")
                # محاولة استعادة من النسخة الاحتياطية
                return self._restore_from_backup()
            except Exception as e:
                st.error(f"❌ خطأ غير متوقع في تحميل الإعدادات: {e}")
                return self._create_default_settings()
        else:
            st.info("🔧 إنشاء إعدادات جديدة باستخدام القيم الافتراضية")
            return self._create_default_settings()

    def _create_default_settings(self) -> Dict[str, Any]:
        """إنشاء إعدادات افتراضية شاملة"""
        default_settings = {
            "APP_INFO": {
                "APP_NAME": "⚖️ منصة قانون العمل الذكية",
                "VERSION": "v25.1",
                "DESCRIPTION": "منصة شاملة للاستشارات القانونية وحساب المستحقات",
                "DEVELOPER": "فريق التطوير القانوني",
                "RELEASE_DATE": "2025-01-01"
            },
            "LANGUAGE": {
                "LANG": "ar",
                "RTL": True,
                "DATE_FORMAT": "YYYY-MM-DD",
                "TIMEZONE": "Asia/Amman"
            },
            "THEME": {
                "THEME": "فاتح",
                "PRIMARY_COLOR": "#667eea",
                "SECONDARY_COLOR": "#764ba2",
                "ACCENT_COLOR": "#10B981"
            },
            "DATA_SOURCES": {
                "WORKBOOK_PATH": "AlyWork_Law_Pro_v2025_v24_ColabStreamlitReady.xlsx",
                "SHEET_URL": "https://docs.google.com/spreadsheets/d/1aCnqHzxWh8RlIgCleHByoCPHMzI1i5fCjrpizcTxGVc/export?format=csv",
                "BACKUP_ENABLED": True,
                "AUTO_SYNC": True
            },
            "PERFORMANCE": {
                "CACHE_ENABLED": True,
                "CACHE_TTL_SECONDS": 600,
                "MAX_FILE_SIZE_MB": 50,
                "AUTO_REFRESH_INTERVAL": 300
            },
            "UI_SETTINGS": {
                "STYLES_LIGHT": "assets/styles_light.css",
                "STYLES_DARK": "assets/styles_dark.css", 
                "ICON_PATH": "assets/icons/",
                "DEFAULT_AVATAR": "assets/images/default_avatar.png",
                "FAVICON": "assets/icons/favicon.ico"
            },
            "AI_FEATURES": {
                "ENABLE_AI": True,
                "MEMORY_PATH": "ai_memory.json",
                "LOGS_PATH": "AI_Analysis_Logs.csv",
                "MAX_HISTORY": 20,
                "MIN_SIMILARITY_THRESHOLD": 0.15,
                "ENABLE_LEARNING": True
            },
            "RECOMMENDATION_SYSTEM": {
                "MAX_CARDS": 6,
                "ENABLE_PERSONALIZATION": True,
                "ROLES": ["العمال", "أصحاب العمل", "مفتشو العمل", "الباحثون والمتدربون"],
                "UPDATE_FREQUENCY": "daily"
            },
            "SECURITY": {
                "ENABLE_VALIDATION": True,
                "MAX_LOGIN_ATTEMPTS": 5,
                "SESSION_TIMEOUT_MINUTES": 60,
                "ENABLE_AUDIT_LOG": True
            },
            "NOTIFICATIONS": {
                "ENABLE_EMAIL_ALERTS": False,
                "ENABLE_BROWSER_NOTIFICATIONS": True,
                "UPDATE_NOTIFICATIONS": True
            },
            "METADATA": {
                "CREATED_AT": datetime.now().isoformat(),
                "LAST_UPDATED": datetime.now().isoformat(),
                "UPDATED_BY": "system",
                "TOTAL_UPDATES": 0
            },
            "FOOTER": {
                "TEXT": f"© {datetime.now().year} منصة قانون العمل الذكية — جميع الحقوق محفوظة",
                "SHOW_VERSION": True,
                "SHOW_DEVELOPER": True
            }
        }
        
        # حفظ الإعدادات الافتراضية
        self._save_settings_to_file(default_settings)
        return default_settings

    def _validate_settings(self, settings: Dict[str, Any]) -> bool:
        """التحقق من صحة هيكل الإعدادات"""
        required_sections = ["APP_INFO", "DATA_SOURCES", "AI_FEATURES"]
        
        for section in required_sections:
            if section not in settings:
                st.error(f"❌ قسم {section} مفقود في الإعدادات")
                return False
        
        # التحقق من المسارات الأساسية
        if not settings.get("DATA_SOURCES", {}).get("WORKBOOK_PATH"):
            st.error("❌ مسار ملف العمل مطلوب")
            return False
            
        return True

    def _restore_from_backup(self) -> Dict[str, Any]:
        """استعادة الإعدادات من النسخة الاحتياطية"""
        if os.path.exists(self.backup_path):
            try:
                with open(self.backup_path, "r", encoding="utf-8") as f:
                    backup_settings = json.load(f)
                st.success("✅ تم استعادة الإعدادات من النسخة الاحتياطية")
                self._log_event("settings_restored", "من النسخة الاحتياطية")
                return backup_settings
            except Exception as e:
                st.error(f"❌ فشل استعادة النسخة الاحتياطية: {e}")
        
        st.info("🔄 إنشاء إعدادات افتراضية جديدة")
        return self._create_default_settings()

    def _save_settings_to_file(self, settings: Dict[str, Any]) -> bool:
        """حفظ الإعدادات إلى الملف مع إنشاء نسخة احتياطية"""
        try:
            # إنشاء نسخة احتياطية أولاً
            if os.path.exists(self.path):
                os.replace(self.path, self.backup_path)
            
            # حفظ الإعدادات الجديدة
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            
            self._log_event("settings_saved", f"تم حفظ {len(settings)} إعداد")
            return True
            
        except Exception as e:
            st.error(f"❌ فشل في حفظ الإعدادات: {e}")
            return False

    def save_settings(self):
        """حفظ الإعدادات الحالية"""
        # تحديث البيانات الوصفية
        self.settings["METADATA"]["LAST_UPDATED"] = datetime.now().isoformat()
        self.settings["METADATA"]["TOTAL_UPDATES"] = self.settings["METADATA"].get("TOTAL_UPDATES", 0) + 1
        
        if self._save_settings_to_file(self.settings):
            st.session_state["config"] = self.settings
            st.success("✅ تم حفظ الإعدادات بنجاح")
        else:
            st.error("❌ فشل في حفظ الإعدادات")

    def get(self, key: str, default: Any = None, section: str = None) -> Any:
        """
        الحصول على قيمة إعداد مع معالجة للمسارات المتداخلة
        
        Args:
            key: المفتاح المطلوب
            default: القيمة الافتراضية
            section: القسم (اختياري للمسارات المتداخلة)
        """
        try:
            if section:
                return self.settings.get(section, {}).get(key, default)
            else:
                # البحث في جميع الأقسام
                for section_name, section_data in self.settings.items():
                    if key in section_data:
                        return section_data[key]
                return default
        except (AttributeError, TypeError):
            return default

    def set(self, key: str, value: Any, section: str = None):
        """تعيين قيمة إعداد"""
        try:
            if section:
                if section not in self.settings:
                    self.settings[section] = {}
                self.settings[section][key] = value
            else:
                # إذا لم يتم تحديد قسم، نضيف إلى البيانات العامة
                self.settings[key] = value
            
            self.save_settings()
            self._log_event("setting_updated", f"{section}.{key} if section else key")
            
        except Exception as e:
            st.error(f"❌ خطأ في تعيين الإعداد: {e}")

    def update(self, new_settings: Dict[str, Any]):
        """تحديث مجموعة إعدادات"""
        if isinstance(new_settings, dict):
            # تحديث متداخل
            for key, value in new_settings.items():
                if isinstance(value, dict) and key in self.settings:
                    self.settings[key].update(value)
                else:
                    self.settings[key] = value
            
            self.save_settings()
            self._log_event("settings_updated", f"تم تحديث {len(new_settings)} إعداد")
        else:
            st.error("⚠️ يجب أن يكون التحديث على شكل قاموس")

    def reset_to_default(self):
        """إعادة التعيين إلى الإعدادات الافتراضية"""
        if st.button("⚠️ تأكيد إعادة التعيين إلى الإعدادات الافتراضية"):
            self.settings = self._create_default_settings()
            st.session_state["config"] = self.settings
            st.success("🔄 تم إعادة التعيين إلى الإعدادات الافتراضية")
            self._log_event("settings_reset", "إلى الإعدادات الافتراضية")

    def export_settings(self, format: str = "json") -> str:
        """تصدير الإعدادات"""
        if format == "json":
            return json.dumps(self.settings, ensure_ascii=False, indent=4)
        else:
            return str(self.settings)

    def get_settings_summary(self) -> Dict[str, Any]:
        """الحصول على ملخص الإعدادات"""
        return {
            "total_sections": len(self.settings),
            "app_name": self.get("APP_NAME", section="APP_INFO"),
            "version": self.get("VERSION", section="APP_INFO"),
            "ai_enabled": self.get("ENABLE_AI", section="AI_FEATURES"),
            "last_updated": self.get("LAST_UPDATED", section="METADATA"),
            "total_updates": self.get("TOTAL_UPDATES", section="METADATA", default=0)
        }

    def _log_event(self, event_type: str, description: str):
        """تسجيل أحداث النظام (يمكن توسعته لاحقاً)"""
        # يمكن إضافة نظام تسجيل متكامل هنا
        pass

# ==============================
# 📊 دوال مساعدة لتحميل البيانات
# ==============================
def safe_load_excel(path: str, required_columns: list = None) -> pd.DataFrame:
    """
    تحميل ملف Excel بأمان مع معالجة متقدمة للأخطاء
    
    Args:
        path: مسار ملف Excel
        required_columns: الأعمدة المطلوبة
        
    Returns:
        DataFrame: البيانات المحملة أو DataFrame فارغ
    """
    if required_columns is None:
        required_columns = ['المادة', 'القسم', 'النص', 'مثال']
    
    if not os.path.exists(path):
        st.warning(f"⚠️ ملف Excel غير موجود: {path}")
        return pd.DataFrame(columns=required_columns)
    
    try:
        # محاولة القراءة بمحركات متعددة
        try:
            df = pd.read_excel(path, engine='openpyxl')
        except:
            df = pd.read_excel(path, engine='xlrd')
        
        # التحقق من الأعمدة المطلوبة
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.warning(f"⚠️ الأعمدة التالية مفقودة: {', '.join(missing_columns)}")
            for col in missing_columns:
                df[col] = ""
        
        # تنظيف البيانات
        df = df[required_columns]
        df.fillna("", inplace=True)
        
        # إزالة الصفوف الفارغة تماماً
        df = df[df.astype(str).apply(lambda x: x.str.strip().ne('').any(), axis=1)]
        
        st.success(f"✅ تم تحميل {len(df)} سجل من {os.path.basename(path)}")
        return df
        
    except Exception as e:
        st.error(f"❌ خطأ في تحميل ملف Excel: {e}")
        return pd.DataFrame(columns=required_columns)

# إنشاء نسخة عامة للاستخدام السريع
def create_settings_manager(path: str = "helpers/config.json") -> SettingsManager:
    """إنشاء مدير إعدادات مع معالجة الأخطاء"""
    try:
        return SettingsManager(path)
    except Exception as e:
        st.error(f"❌ فشل في إنشاء مدير الإعدادات: {e}")
        # إرجاع مدير بإعدادات افتراضية
        manager = SettingsManager.__new__(SettingsManager)
        manager.settings = manager._create_default_settings()
        return manager

# مثال للاستخدام
if __name__ == "__main__":
    # اختبار الوظائف
    settings_mgr = SettingsManager()
    print("الإعدادات المحملة:", settings_mgr.get_settings_summary())