import pandas as pd
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MiniLegalAI:
    def __init__(self, workbook_path=None):
        """
        تهيئة المساعد الذكي وربط قاعدة البيانات القانونية.
        :param workbook_path: مسار ملف Excel الرئيسي (AlyWork_Law_Pro)
        """
        self.workbook_path = workbook_path or "AlyWork_Law_Pro_v2025_v24_ColabStreamlitReady.xlsx"
        self.db = self.load_database()
        self.vectorizer = None
        self.tfidf_matrix = None
        self.build_tfidf_matrix()
    
    def load_database(self):
        """
        تحميل قاعدة البيانات من ملف Excel.
        يتوقع وجود الأعمدة: المادة، القسم، النص، مثال
        """
        if not os.path.exists(self.workbook_path):
            print(f"⚠️ ملف قاعدة البيانات غير موجود: {self.workbook_path}")
            return pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال'])
        try:
            df = pd.read_excel(self.workbook_path, engine='openpyxl')
            df.fillna("", inplace=True)
            return df
        except Exception as e:
            print(f"⚠️ خطأ عند تحميل قاعدة البيانات: {e}")
            return pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال'])
    
    def preprocess_text(self, text):
        """
        تنظيف النصوص: حذف علامات الترقيم والأحرف الخاصة
        """
        text = str(text).strip()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def build_tfidf_matrix(self):
        """
        بناء مصفوفة TF-IDF للنصوص في قاعدة البيانات
        """
        if self.db.empty:
            return
        corpus = self.db['النص'].apply(self.preprocess_text).tolist()
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def advanced_search(self, query, top_n=1):
        """
        البحث الذكي في قاعدة البيانات باستخدام TF-IDF وCosine Similarity
        :param query: الاستعلام النصي
        :param top_n: عدد النتائج الأعلى تطابقًا
        :return: (answer, reference, example)
        """
        if self.db.empty or self.tfidf_matrix is None:
            return "⚠️ قاعدة البيانات فارغة.", "", ""
        
        query_clean = self.preprocess_text(query)
        query_vec = self.vectorizer.transform([query_clean])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        top_indices = similarities.argsort()[::-1][:top_n]
        best_score = similarities[top_indices[0]]
        
        if best_score == 0:
            return "⚠️ لم يتم العثور على تطابق مباشر في قاعدة البيانات.", "", ""
        
        row = self.db.iloc[top_indices[0]]
        answer = row['النص']
        reference = f"المادة {row['المادة']} - القسم: {row['القسم']}"
        example = row['مثال'] if 'مثال' in row else "لا يوجد مثال متاح."
        return answer, reference, example