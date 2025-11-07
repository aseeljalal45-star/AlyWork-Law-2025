import pandas as pd
import streamlit as st
import os
import requests
from typing import Union, Optional, Dict, Any
from datetime import datetime
import tempfile

# ==============================
# 📂 مدير تحميل البيانات المتقدم
# ==============================
class DataLoader:
    """
    🚀 مدير تحميل البيانات الذكي - الإصدار المحسن
    
    يدعم مصادر متعددة مع ميزات متقدمة للأداء والمرونة
    """
    
    def __init__(self):
        self.load_history = []
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json']
        self.max_file_size_mb = 50
        
    @st.cache_data(ttl=600, show_spinner="جاري تحميل البيانات...")
    def load_data(_self, source_path: str, **kwargs) -> pd.DataFrame:
        """
        تحميل البيانات من مصادر متعددة مع معالجة متقدمة للأخطاء
        
        Args:
            source_path (str): مسار الملف أو الرابط
            **kwargs: إعدادات إضافية لكل نوع ملف
            
        Returns:
            pd.DataFrame: البيانات المحملة أو DataFrame فارغ
        """
        try:
            # تسجيل محاولة التحميل
            _self._log_loading_attempt(source_path)
            
            # تحديد نوع المصدر وتوجيه للدالة المناسبة
            if _self._is_google_sheets_url(source_path):
                df = _self._load_google_sheets(source_path, **kwargs)
            elif _self._is_http_url(source_path):
                df = _self._load_http_data(source_path, **kwargs)
            elif source_path.endswith('.xlsx') or source_path.endswith('.xls'):
                df = _self._load_excel_file(source_path, **kwargs)
            elif source_path.endswith('.csv'):
                df = _self._load_csv_file(source_path, **kwargs)
            elif source_path.endswith('.json'):
                df = _self._load_json_file(source_path, **kwargs)
            else:
                raise ValueError(f"❌ صيغة الملف غير مدعومة: {source_path}")
            
            # معالجة ما بعد التحميل
            if not df.empty:
                df = _self._post_process_data(df, source_path)
                _self._log_successful_load(source_path, len(df))
                
            return df
            
        except Exception as e:
            _self._log_loading_error(source_path, str(e))
            return pd.DataFrame()

    def _is_google_sheets_url(self, url: str) -> bool:
        """التعرف على روابط Google Sheets"""
        return "docs.google.com/spreadsheets" in url

    def _is_http_url(self, url: str) -> bool:
        """التعرف على الروابط العامة"""
        return url.startswith(('http://', 'https://'))

    def _load_google_sheets(self, url: str, **kwargs) -> pd.DataFrame:
        """تحميل بيانات من Google Sheets"""
        try:
            # تحويل رابط العرض إلى رابط تصدير CSV
            if "/edit" in url:
                url = url.replace("/edit", "/export?format=csv")
            elif "export?format=csv" not in url:
                sheet_id = self._extract_google_sheets_id(url)
                if sheet_id:
                    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            
            df = pd.read_csv(url, **kwargs)
            st.success(f"📊 تم تحميل {len(df)} صف من Google Sheets")
            return df
            
        except Exception as e:
            st.error(f"❌ خطأ في تحميل Google Sheets: {e}")
            return pd.DataFrame()

    def _extract_google_sheets_id(self, url: str) -> Optional[str]:
        """استخراج معرف Google Sheets من الرابط"""
        import re
        pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def _load_http_data(self, url: str, **kwargs) -> pd.DataFrame:
        """تحميل بيانات من روابط HTTP عامة"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # تحديد النوع بناءً على المحتوى أو الامتداد
            if url.endswith('.csv'):
                import io
                df = pd.read_csv(io.StringIO(response.text), **kwargs)
            elif url.endswith('.json'):
                df = pd.read_json(io.StringIO(response.text), **kwargs)
            else:
                # محاولة التحميل كـ CSV افتراضيًا
                import io
                df = pd.read_csv(io.StringIO(response.text), **kwargs)
                
            st.success(f"🌐 تم تحميل {len(df)} صف من الرابط")
            return df
            
        except Exception as e:
            st.error(f"❌ خطأ في تحميل البيانات من الرابط: {e}")
            return pd.DataFrame()

    def _load_excel_file(self, file_path: str, **kwargs) -> pd.DataFrame:
        """تحميل بيانات من ملف Excel"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"الملف غير موجود: {file_path}")
        
        # فحص حجم الملف
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            st.warning(f"⚠️ حجم الملف كبير ({file_size_mb:.1f} MB). قد يستغرق التحميل وقتًا أطول.")
        
        # محاولة المحركات المختلفة
        engines = ['openpyxl', 'xlrd']
        for engine in engines:
            try:
                df = pd.read_excel(file_path, engine=engine, **kwargs)
                st.success(f"📗 تم تحميل {len(df)} صف من ملف Excel")
                return df
            except Exception as e:
                continue
        
        raise Exception("فشل تحميل ملف Excel مع جميع المحركات المتاحة")

    def _load_csv_file(self, file_path: str, **kwargs) -> pd.DataFrame:
        """تحميل بيانات من ملف CSV"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"الملف غير موجود: {file_path}")
        
        # إعدادات CSV افتراضية محسنة للعربية
        default_kwargs = {
            'encoding': 'utf-8',
            'sep': ',',
            'skipinitialspace': True
        }
        default_kwargs.update(kwargs)
        
        try:
            df = pd.read_csv(file_path, **default_kwargs)
            st.success(f"📄 تم تحميل {len(df)} صف من ملف CSV")
            return df
        except UnicodeDecodeError:
            # محاولة بتشفيرات أخرى
            for encoding in ['latin1', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, **kwargs)
                    st.success(f"📄 تم تحميل {len(df)} صف من ملف CSV (بترميز {encoding})")
                    return df
                except UnicodeDecodeError:
                    continue
            raise Exception("فشل تحميل ملف CSV مع جميع التشفيرات المتاحة")

    def _load_json_file(self, file_path: str, **kwargs) -> pd.DataFrame:
        """تحميل بيانات من ملف JSON"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"الملف غير موجود: {file_path}")
        
        try:
            df = pd.read_json(file_path, **kwargs)
            st.success(f"📋 تم تحميل {len(df)} صف من ملف JSON")
            return df
        except Exception as e:
            raise Exception(f"خطأ في تحميل ملف JSON: {e}")

    def _post_process_data(self, df: pd.DataFrame, source_path: str) -> pd.DataFrame:
        """معالجة البيانات بعد التحميل"""
        # إزالة الصفوف الفارغة تمامًا
        initial_count = len(df)
        df = df.dropna(how='all')
        
        if len(df) < initial_count:
            st.info(f"🧹 تم إزالة {initial_count - len(df)} صف فارغ")
        
        # إعادة تعيين الفهرس
        df = df.reset_index(drop=True)
        
        # تحويل أسماء الأعمدة إلى نص في حالة وجود أي قيم غير نصية
        df.columns = df.columns.astype(str)
        
        # ملء القيم الفارغة في الأعمدة النصية
        text_columns = df.select_dtypes(include=['object']).columns
        df[text_columns] = df[text_columns].fillna('')
        
        return df

    def _log_loading_attempt(self, source_path: str):
        """تسجيل محاولة التحميل"""
        self.load_history.append({
            'timestamp': datetime.now().isoformat(),
            'source': source_path,
            'type': 'attempt',
            'status': 'started'
        })

    def _log_successful_load(self, source_path: str, row_count: int):
        """تسجيل التحميل الناجح"""
        self.load_history.append({
            'timestamp': datetime.now().isoformat(),
            'source': source_path,
            'type': 'success',
            'status': 'completed',
            'row_count': row_count
        })

    def _log_loading_error(self, source_path: str, error_msg: str):
        """تسجيل خطأ التحميل"""
        self.load_history.append({
            'timestamp': datetime.now().isoformat(),
            'source': source_path,
            'type': 'error',
            'status': 'failed',
            'error': error_msg
        })
        st.error(f"❌ فشل تحميل البيانات من {source_path}")

    def get_load_history(self, last_n: int = 10) -> list:
        """الحصول على سجل التحميل"""
        return self.load_history[-last_n:]

    def clear_cache(self):
        """مسح التخزين المؤقت"""
        st.cache_data.clear()
        st.success("🗑️ تم مسح التخزين المؤقت للبيانات")

# ==============================
# 🎯 دوال سريعة للاستخدام
# ==============================
@st.cache_data(ttl=600)
def load_data_smart(source_path: str, **kwargs) -> pd.DataFrame:
    """
    دالة سريعة لتحميل البيانات (للتوافق مع الكود الحالي)
    
    Args:
        source_path (str): مسار الملف أو الرابط
        **kwargs: إعدادات إضافية
        
    Returns:
        pd.DataFrame: البيانات المحملة
    """
    loader = DataLoader()
    return loader.load_data(source_path, **kwargs)

def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    إنشاء ملخص للبيانات المحملة
    
    Args:
        df (pd.DataFrame): البيانات
        
    Returns:
        dict: ملخص البيانات
    """
    if df.empty:
        return {"status": "empty", "message": "لا توجد بيانات"}
    
    return {
        "status": "loaded",
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": df.columns.tolist(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024),
        "sample_data": df.head(3).to_dict('records')
    }

# مثال للاستخدام
if __name__ == "__main__":
    # اختبار الدوال
    st.title("🧪 اختبار تحميل البيانات")
    
    # اختبار مع ملف مثال
    test_path = "example_data.csv"
    df = load_data_smart(test_path)
    
    if not df.empty:
        summary = get_data_summary(df)
        st.json(summary)