import pandas as pd
import streamlit as st

class DataLoader:
    @st.cache_data(ttl=600)
    def load_data(_self, source_path):
        """تحميل البيانات من مصادر متعددة"""
        try:
            if source_path.startswith("http"):
                df = pd.read_csv(source_path)
                st.success(f"✅ تم تحميل {len(df)} صف من الرابط")
            elif source_path.endswith(".xlsx"):
                df = pd.read_excel(source_path, engine='openpyxl')
                st.success(f"✅ تم تحميل {len(df)} صف من ملف Excel")
            else:
                df = pd.DataFrame()
            
            return df
        except Exception as e:
            st.error(f"❌ خطأ في تحميل البيانات: {e}")
            return pd.DataFrame()