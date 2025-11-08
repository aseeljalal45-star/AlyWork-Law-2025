import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

class MiniLegalAI:
    def __init__(self, workbook_path=None):
        self.workbook_path = workbook_path
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None
        self.db = pd.DataFrame()
        
        if workbook_path and os.path.exists(workbook_path):
            self.load_database_from_excel()
            self.build_tfidf_matrix()

    def load_database_from_excel(self):
        """تحميل قاعدة البيانات"""
        try:
            self.db = pd.read_excel(self.workbook_path, engine='openpyxl')
            required_cols = ['المادة', 'القسم', 'النص', 'مثال']
            for col in required_cols:
                if col not in self.db.columns:
                    self.db[col] = ""
            self.db.fillna("", inplace=True)
            st.success(f"✅ تم تحميل {len(self.db)} سجل قانوني")
        except Exception as e:
            st.error(f"❌ خطأ في تحميل البيانات: {e}")

    def build_tfidf_matrix(self):
        """بناء مصفوفة البحث"""
        if not self.db.empty:
            corpus = self.db['النص'].fillna('').astype(str).tolist()
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def advanced_search(self, query, top_n=3):
        """بحث ذكي في القوانين"""
        if self.db.empty or self.tfidf_matrix is None:
            return []
        
        try:
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            top_indices = similarities.argsort()[::-1][:top_n]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # عتبة الدقة
                    row = self.db.iloc[idx]
                    results.append({
                        "text": row.get("النص", ""),
                        "example": row.get("مثال", ""),
                        "reference": f"المادة {row.get('المادة', '')} - القسم: {row.get('القسم', '')}",
                        "score": round(similarities[idx] * 100, 1)
                    })
            
            return results
        except Exception as e:
            st.error(f"❌ خطأ في البحث: {e}")
            return []

    def reload(self):
        """إعادة تحميل البيانات"""
        self.load_database_from_excel()
        self.build_tfidf_matrix()
        st.success("🔄 تم تحديث البيانات بنجاح")