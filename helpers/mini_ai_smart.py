import pandas as pd
import os, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

class MiniLegalAI:
    def __init__(self, workbook_path=None):
        """تهيئة المساعد الذكي وربط قاعدة البيانات القانونية."""
        config = st.session_state.get("config", {})
        self.ai_enabled = config.get("AI", {}).get("ENABLE", True)
        if not self.ai_enabled:
            st.warning("🤖 المساعد الذكي معطل من إعدادات النظام.")
        
        self.workbook_path = workbook_path or config.get("WORKBOOK_PATH", "")
        self.vectorizer = None
        self.tfidf_matrix = None
        self.db = pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال'])  # افتراضي

        # إذا الملف موجود، يتم تحميله مباشرة
        if self.workbook_path and os.path.exists(self.workbook_path):
            self.load_database_from_excel()
            self.build_tfidf_matrix()

    # ==============================
    # تحميل قاعدة البيانات
    # ==============================
    def load_database_from_excel(self, path=None):
        path = path or self.workbook_path
        if not os.path.exists(path):
            st.warning(f"⚠️ ملف قاعدة البيانات غير موجود: {path}")
            self.db = pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال'])
            return
        try:
            df = pd.read_excel(path, engine='openpyxl')
            for col in ['المادة', 'القسم', 'النص', 'مثال']:
                if col not in df.columns:
                    df[col] = ""
            df = df[['المادة', 'القسم', 'النص', 'مثال']]
            df.fillna("", inplace=True)
            self.db = df
            st.session_state['ai_db'] = df  # حفظ نسخة في session state
        except Exception as e:
            st.error(f"⚠️ خطأ عند تحميل قاعدة البيانات: {e}")
            self.db = pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال'])

    # ==============================
    # تنظيف النصوص
    # ==============================
    @staticmethod
    def preprocess_text(text):
        text = str(text).strip()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text

    # ==============================
    # بناء مصفوفة TF-IDF
    # ==============================
    def build_tfidf_matrix(self):
        if self.db.empty:
            return
        corpus = self.db['النص'].apply(self.preprocess_text).tolist()
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    # ==============================
    # البحث الذكي
    # ==============================
    def advanced_search(self, query, top_n=1):
        if not self.ai_enabled:
            return "🤖 المساعد الذكي معطل.", "", ""
        if self.db.empty or self.tfidf_matrix is None:
            return "⚠️ قاعدة البيانات فارغة.", "", ""

        query_vec = self.vectorizer.transform([self.preprocess_text(query)])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = similarities.argsort()[::-1][:top_n]

        if similarities[top_indices[0]] == 0:
            return "⚠️ لم يتم العثور على تطابق مباشر في قاعدة البيانات.", "", ""

        best_row = self.db.iloc[top_indices[0]]
        score = round(similarities[top_indices[0]] * 100, 2)
        return (
            best_row.get("النص", ""),
            f"المادة {best_row.get('المادة', '')} - القسم: {best_row.get('القسم', '')} (دقة {score}%)",
            best_row.get("مثال", "")
        )

    # ==============================
    # إعادة تحميل القاعدة
    # ==============================
    def reload(self, new_path=None):
        if new_path:
            self.workbook_path = new_path
        self.load_database_from_excel()
        self.build_tfidf_matrix()
        st.success("✅ تم تحديث قاعدة البيانات بنجاح.")