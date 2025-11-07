import pandas as pd
import os, re
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MiniLegalAI:
    def __init__(self, workbook_path=None):
        """تهيئة المساعد الذكي وربط قاعدة البيانات القانونية."""
        # جلب الإعدادات من config
        config = st.session_state.get("config", {})
        self.ai_enabled = config.get("AI", {}).get("ENABLE", True)
        if not self.ai_enabled:
            st.warning("🤖 المساعد الذكي معطل من إعدادات النظام.")
            return

        self.workbook_path = workbook_path or config.get("WORKBOOK_PATH", "AlyWork_Law_Pro_v2025_v24_ColabStreamlitReady.xlsx")
        self.memory_path = config.get("AI", {}).get("MEMORY_PATH", "ai_memory.json")
        self.logs_path = config.get("AI", {}).get("LOGS_PATH", "AI_Analysis_Logs.csv")
        self.max_history = config.get("AI", {}).get("MAX_HISTORY", 20)

        # تحميل قاعدة البيانات وبناء المصفوفة
        self.db = self.load_database()
        self.vectorizer = None
        self.tfidf_matrix = None
        self.build_tfidf_matrix()

    # ==============================
    # تحميل قاعدة البيانات
    # ==============================
    @st.cache_data(show_spinner=False, allow_output_mutation=True)
    def load_database(self):
        """تحميل ملف قاعدة البيانات القانونية."""
        if not os.path.exists(self.workbook_path):
            st.warning(f"⚠️ ملف قاعدة البيانات غير موجود: {self.workbook_path}")
            return pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال'])
        try:
            with st.spinner("⏳ جاري تحميل قاعدة البيانات القانونية..."):
                df = pd.read_excel(self.workbook_path, engine='openpyxl')
                df.fillna("", inplace=True)
                return df
        except Exception as e:
            st.error(f"⚠️ خطأ عند تحميل قاعدة البيانات: {e}")
            return pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال'])

    # ==============================
    # تنظيف النصوص
    # ==============================
    def preprocess_text(self, text):
        text = str(text).strip()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text

    # ==============================
    # بناء مصفوفة TF-IDF
    # ==============================
    @st.cache_data(show_spinner=False, allow_output_mutation=True)
    def build_tfidf_matrix(self):
        """بناء مصفوفة TF-IDF للنصوص القانونية."""
        if self.db.empty:
            return
        text_col = next((c for c in self.db.columns if "نص" in c), None)
        if not text_col:
            st.error("⚠️ لم يتم العثور على عمود يحتوي على نصوص قانونية في الملف.")
            return
        corpus = self.db[text_col].apply(self.preprocess_text).tolist()
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    # ==============================
    # البحث الذكي
    # ==============================
    def advanced_search(self, query, top_n=1):
        """البحث عن النصوص الأكثر تطابقًا مع الاستعلام."""
        if not self.ai_enabled:
            return "🤖 المساعد الذكي معطل.", "", ""

        if self.db.empty or self.tfidf_matrix is None:
            return "⚠️ قاعدة البيانات فارغة.", "", ""

        query_clean = self.preprocess_text(query)
        query_vec = self.vectorizer.transform([query_clean])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = similarities.argsort()[::-1][:top_n]

        if similarities[top_indices[0]] == 0:
            return "⚠️ لم يتم العثور على تطابق مباشر في قاعدة البيانات.", "", ""

        results = []
        for i in top_indices:
            row = self.db.iloc[i]
            score = round(similarities[i] * 100, 2)
            results.append({
                "النص": row.get("النص", ""),
                "المادة": row.get("المادة", ""),
                "القسم": row.get("القسم", ""),
                "مثال": row.get("مثال", ""),
                "التطابق": f"{score}%"
            })

        best = results[0]
        return best["النص"], f"المادة {best['المادة']} - القسم: {best['القسم']} (دقة {best['التطابق']})", best["مثال"]

    # ==============================
    # إعادة تحميل القاعدة
    # ==============================
    def reload(self, new_path=None):
        """إعادة تحميل قاعدة البيانات بعد تغيير الملف أو التحديث."""
        if new_path:
            self.workbook_path = new_path
        self.db = self.load_database()
        self.build_tfidf_matrix()
        st.success("✅ تم تحديث قاعدة البيانات بنجاح.")