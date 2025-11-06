import pandas as pd
import streamlit as st

# ==============================
# 📂 دالة تحميل البيانات الذكية
# ==============================
@st.cache_data(ttl=600)
def load_data(source_path: str) -> pd.DataFrame:
    """
    تحميل البيانات من مصدر محدد (CSV، XLSX، Google Sheets).
    
    Args:
        source_path (str): رابط أو مسار الملف.
    
    Returns:
        pd.DataFrame: DataFrame يحتوي على البيانات، أو فارغ عند حدوث خطأ.
    """
    try:
        if source_path.startswith("http"):
            # دعم Google Sheets CSV links
            df = pd.read_csv(source_path)
            st.success(f"✅ تم تحميل البيانات من الرابط بنجاح ({len(df)} صف).")
            return df

        elif source_path.endswith(".xlsx"):
            df = pd.read_excel(source_path, engine="openpyxl")
            st.success(f"✅ تم تحميل ملف Excel بنجاح ({len(df)} صف).")
            return df

        elif source_path.endswith(".csv"):
            df = pd.read_csv(source_path)
            st.success(f"✅ تم تحميل ملف CSV بنجاح ({len(df)} صف).")
            return df

        else:
            raise ValueError("⚠️ صيغة الملف غير مدعومة. استخدم CSV أو XLSX أو رابط Google Sheets CSV.")

    except FileNotFoundError:
        st.error(f"❌ لم يتم العثور على الملف: {source_path}")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        st.error(f"❌ الملف فارغ: {source_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء تحميل البيانات: {e}")
        return pd.DataFrame()