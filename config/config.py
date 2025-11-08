import json
import os
import streamlit as st
from datetime import datetime
from typing import Any, Dict, Optional, List, Union
from pathlib import Path

class ConfigManager:
    """
    🎛️ مدير الإعدادات المتقدم - الإصدار المحسن
    
    يدير إعدادات التطبيق مع ميزات متقدمة للأمان والمرونة والنسخ الاحتياطي
    """
    
    def __init__(self, path: str = "helpers/config.json"):
        """
        تهيئة مدير الإعدادات
        
        Args:
            path (str): مسار ملف الإعدادات
        """
        self.path = Path(path)
        self.backup_path = self.path.with_suffix('.json.backup')
        self.config = self.load_config()
        
        # تكامل مع Streamlit session state
        st.session_state["config"] = self.config
        
        # تسجيل عملية التهيئة
        self._log_event("system_initialized", f"تم تهيئة مدير الإعدادات من {self.path}")

    def load_config(self) -> Dict[str, Any]:
        """
        تحميل الإعدادات من الملف مع معالجة متقدمة للأخطاء
        
        Returns:
            Dict[str, Any]: الإعدادات المحملة
        """
        # محاولة تحميل الإعدادات الحالية
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # التحقق من صحة الهيكل الأساسي
                if self._validate_config(config):
                    st.success("✅ تم تحميل الإعدادات بنجاح")
                    self._log_event("config_loaded", f"تم تحميل {len(config)} إعداد")
                    return config
                else:
                    st.warning("⚠️ إعدادات غير صالحة، سيتم استخدام الإعدادات الافتراضية")
                    return self._create_default_config()
                    
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                st.error(f"❌ خطأ في تنسيق ملف الإعدادات: {e}")
                # محاولة استعادة من النسخة الاحتياطية
                return self._restore_from_backup()
            except Exception as e:
                st.error(f"❌ خطأ غير متوقع في تحميل الإعدادات: {e}")
                return self._create_default_config()
        else:
            st.info("🔧 إنشاء إعدادات جديدة باستخدام القيم الافتراضية")
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """
        إنشاء إعدادات افتراضية شاملة
        
        Returns:
            Dict[str, Any]: الإعدادات الافتراضية
        """
        default_config = {
            "APP_INFO": {
                "APP_NAME": "⚖️ منصة قانون العمل الذكية",
                "VERSION": "v25.1",
                "DESCRIPTION": "منصة شاملة للاستشارات القانونية وحساب المستحقات",
                "DEVELOPER": "فريق التطوير القانوني",
                "RELEASE_DATE": "2025-01-01",
                "SUPPORT_EMAIL": "support@alyworklaw.com"
            },
            "LANGUAGE": {
                "LANG": "ar",
                "RTL": True,
                "DATE_FORMAT": "YYYY-MM-DD",
                "TIMEZONE": "Asia/Amman"
            },
            "THEME": {
                "THEME": "فاتح",
                "PRIMARY_COLOR": "#1E3A8A",
                "SECONDARY_COLOR": "#2563EB",
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
                "MAX_FILE_SIZE_MB": 50
            },
            "UI_SETTINGS": {
                "STYLES_LIGHT": "assets/styles_official.css",
                "STYLES_DARK": "assets/styles_dark.css", 
                "ICON_PATH": "assets/icons/"
            },
            "AI_FEATURES": {
                "ENABLE_AI": True,
                "MEMORY_PATH": "ai_memory.json",
                "LOGS_PATH": "AI_Analysis_Logs.csv",
                "MAX_HISTORY": 20,
                "MIN_SIMILARITY_THRESHOLD": 0.15
            },
            "RECOMMENDATION_SYSTEM": {
                "MAX_CARDS": 6,
                "ROLES": ["العمال", "أصحاب العمل", "مفتشو العمل", "الباحثون والمتدربون"]
            },
            "NAVIGATION": {
                "SIDEBAR_MENU": [
                    {
                        "id": "home",
                        "label": "🏠 الصفحة الرئيسية",
                        "function": "show_home",
                        "icon": "house"
                    },
                    {
                        "id": "workers",
                        "label": "👷 قسم العمال", 
                        "function": "workers_section",
                        "icon": "person"
                    }
                ]
            },
            "METADATA": {
                "CREATED_AT": datetime.now().isoformat(),
                "LAST_UPDATED": datetime.now().isoformat(),
                "UPDATED_BY": "system",
                "TOTAL_UPDATES": 0
            },
            "FOOTER": {
                "TEXT": "© 2025 منصة قانون العمل الذكية — جميع الحقوق محفوظة",
                "SHOW_VERSION": True
            }
        }
        
        # حفظ الإعدادات الافتراضية
        self._save_config_to_file(default_config)
        return default_config

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        التحقق من صحة هيكل الإعدادات
        
        Args:
            config (Dict[str, Any]): الإعدادات للتحقق
            
        Returns:
            bool: True إذا كانت صالحة
        """
        required_sections = ["APP_INFO", "DATA_SOURCES", "AI_FEATURES"]
        
        for section in required_sections:
            if section not in config:
                st.error(f"❌ قسم {section} مفقود في الإعدادات")
                return False
        
        # التحقق من المسارات الأساسية
        if not config.get("DATA_SOURCES", {}).get("WORKBOOK_PATH"):
            st.error("❌ مسار ملف العمل مطلوب")
            return False
            
        return True

    def _restore_from_backup(self) -> Dict[str, Any]:
        """
        استعادة الإعدادات من النسخة الاحتياطية
        
        Returns:
            Dict[str, Any]: الإعدادات المستعادة
        """
        if self.backup_path.exists():
            try:
                with open(self.backup_path, "r", encoding="utf-8") as f:
                    backup_config = json.load(f)
                st.success("✅ تم استعادة الإعدادات من النسخة الاحتياطية")
                self._log_event("config_restored", "من النسخة الاحتياطية")
                return backup_config
            except Exception as e:
                st.error(f"❌ فشل استعادة النسخة الاحتياطية: {e}")
        
        st.info("🔄 إنشاء إعدادات افتراضية جديدة")
        return self._create_default_config()

    def _save_config_to_file(self, config: Dict[str, Any]) -> bool:
        """
        حفظ الإعدادات إلى الملف مع إنشاء نسخة احتياطية
        
        Args:
            config (Dict[str, Any]): الإعدادات للحفظ
            
        Returns:
            bool: True إذا تم الحفظ بنجاح
        """
        try:
            # إنشاء النسخة الاحتياطية أولاً
            if self.path.exists():
                import shutil
                shutil.copy2(self.path, self.backup_path)
            
            # التأكد من وجود المجلد
            self.path.parent.mkdir(parents=True, exist_ok=True)
            
            # حفظ الإعدادات الجديدة
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            self._log_event("config_saved", f"تم حفظ {len(config)} إعداد")
            return True
            
        except Exception as e:
            st.error(f"❌ فشل في حفظ الإعدادات: {e}")
            return False

    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """
        حفظ الإعدادات الحالية
        
        Args:
            config (Optional[Dict[str, Any]]): إعدادات مخصصة للحفظ
        """
        config_to_save = config or self.config
        
        # تحديث البيانات الوصفية
        if "METADATA" in config_to_save:
            config_to_save["METADATA"]["LAST_UPDATED"] = datetime.now().isoformat()
            config_to_save["METADATA"]["TOTAL_UPDATES"] = config_to_save["METADATA"].get("TOTAL_UPDATES", 0) + 1
        
        if self._save_config_to_file(config_to_save):
            self.config = config_to_save
            st.session_state["config"] = self.config
            st.success("✅ تم حفظ الإعدادات بنجاح")
        else:
            st.error("❌ فشل في حفظ الإعدادات")

    def get(self, key: str, default: Any = None, section: Optional[str] = None) -> Any:
        """
        الحصول على قيمة إعداد
        
        Args:
            key (str): المفتاح المطلوب
            default (Any): القيمة الافتراضية
            section (Optional[str]): القسم (اختياري)
            
        Returns:
            Any: القيمة المطلوبة
        """
        try:
            if section:
                return self.config.get(section, {}).get(key, default)
            else:
                # البحث في جميع الأقسام
                for section_name, section_data in self.config.items():
                    if isinstance(section_data, dict) and key in section_data:
                        return section_data[key]
                return default
        except (AttributeError, TypeError):
            return default

    def set(self, key: str, value: Any, section: Optional[str] = None):
        """
        تعيين قيمة إعداد
        
        Args:
            key (str): المفتاح
            value (Any): القيمة
            section (Optional[str]): القسم
        """
        try:
            if section:
                if section not in self.config:
                    self.config[section] = {}
                self.config[section][key] = value
            else:
                # إذا لم يتم تحديد قسم، نضيف إلى المستوى الرئيسي
                self.config[key] = value
            
            self.save_config()
            self._log_event("setting_updated", f"{section}.{key}" if section else key)
            
        except Exception as e:
            st.error(f"❌ خطأ في تعيين الإعداد: {e}")

    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """
        الوصول للقيم المتداخلة بسهولة
        
        Args:
            *keys (str): مسار المفاتيح المتداخلة
            default (Any): القيمة الافتراضية
            
        Returns:
            Any: القيمة المطلوبة
        """
        try:
            current = self.config
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            return current
        except (AttributeError, TypeError, KeyError):
            return default

    def update(self, new_config: Dict[str, Any]):
        """
        تحديث مجموعة إعدادات
        
        Args:
            new_config (Dict[str, Any]): الإعدادات الجديدة
        """
        if isinstance(new_config, dict):
            # تحديث متداخل للحفاظ على الهيكل
            for key, value in new_config.items():
                if isinstance(value, dict) and key in self.config and isinstance(self.config[key], dict):
                    self.config[key].update(value)
                else:
                    self.config[key] = value
            
            self.save_config()
            self._log_event("config_updated", f"تم تحديث {len(new_config)} إعداد")
        else:
            st.error("⚠️ يجب أن يكون التحديث على شكل قاموس")

    def reset_to_default(self):
        """إعادة التعيين إلى الإعدادات الافتراضية"""
        if st.button("⚠️ تأكيد إعادة التعيين إلى الإعدادات الافتراضية", key="reset_config"):
            self.config = self._create_default_config()
            st.session_state["config"] = self.config
            st.success("🔄 تم إعادة التعيين إلى الإعدادات الافتراضية")
            self._log_event("config_reset", "إلى الإعدادات الافتراضية")

    def export_config(self, format: str = "json") -> str:
        """
        تصدير الإعدادات
        
        Args:
            format (str): تنسيق التصدير
            
        Returns:
            str: الإعدادات مصدرة
        """
        if format == "json":
            return json.dumps(self.config, ensure_ascii=False, indent=4)
        else:
            return str(self.config)

    def get_config_summary(self) -> Dict[str, Any]:
        """
        الحصول على ملخص الإعدادات
        
        Returns:
            Dict[str, Any]: ملخص الإعدادات
        """
        return {
            "total_sections": len(self.config),
            "app_name": self.get_nested("APP_INFO", "APP_NAME"),
            "version": self.get_nested("APP_INFO", "VERSION"),
            "ai_enabled": self.get_nested("AI_FEATURES", "ENABLE_AI"),
            "last_updated": self.get_nested("METADATA", "LAST_UPDATED"),
            "total_updates": self.get_nested("METADATA", "TOTAL_UPDATES", default=0)
        }

    def _log_event(self, event_type: str, description: str):
        """
        تسجيل أحداث النظام
        
        Args:
            event_type (str): نوع الحدث
            description (str): وصف الحدث
        """
        # يمكن إضافة نظام تسجيل متكامل هنا
        print(f"🔧 [{event_type}] {description}")

# دالة مساعدة للاستخدام السريع
def create_config_manager(path: str = "helpers/config.json") -> ConfigManager:
    """
    إنشاء مدير إعدادات مع معالجة الأخطاء
    
    Args:
        path (str): مسار ملف الإعدادات
        
    Returns:
        ConfigManager: مدير الإعدادات
    """
    try:
        return ConfigManager(path)
    except Exception as e:
        st.error(f"❌ فشل في إنشاء مدير الإعدادات: {e}")
        # إرجاع مدير بإعدادات افتراضية
        manager = ConfigManager.__new__(ConfigManager)
        manager.config = manager._create_default_config()
        return manager

# مثال للاستخدام
if __name__ == "__main__":
    # اختبار الوظائف
    config_mgr = ConfigManager()
    summary = config_mgr.get_config_summary()
    print("ملخص الإعدادات:", summary)