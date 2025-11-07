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
        # إذا لم يتم تحديد المسار، يستخدم اسم الملف الافتراضي
        self.workbook_path = workbook_path or "AlyWork_Law_Pro_v2025_v24_ColabStreamlitReady.xlsx"
        self.db = self.load_database()
        self.vectorizer = None
        self.tfidf_matrix = None
        
        if not self.db.empty:
            self.build_tfidf_matrix()

    def load_database(self):
        """
        تحميل قاعدة البيانات من ملف Excel.
        يتوقع وجود الأعمدة: المادة، القسم، النص، مثال
        """
        try:
            if not os.path.exists(self.workbook_path):
                print(f"⚠️ ملف قاعدة البيانات غير موجود: {self.workbook_path}")
                return pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال'])
            
            df = pd.read_excel(self.workbook_path, engine='openpyxl')
            # تنظيف الأعمدة الفارغة وتعبئتها
            df.fillna("", inplace=True)
            
            # التحقق من وجود الأعمدة المطلوبة
            required_cols = ['المادة', 'القسم', 'النص']
            for col in required_cols:
                if col not in df.columns:
                    print(f"⚠️ العمود '{col}' مفقود في قاعدة البيانات.")
                    df[col] = ""
            
            # إنشاء عمود "مثال" إن لم يكن موجودًا
            if 'مثال' not in df.columns:
                df['مثال'] = ""
            
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
            print("⚠️ لا يمكن بناء مصفوفة TF-IDF لأن قاعدة البيانات فارغة.")
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
            return "⚠️ قاعدة البيانات غير جاهزة للبحث.", "", ""
        
        if not query.strip():
            return "⚠️ يرجى إدخال نص للبحث.", "", ""
        
        try:
            query_clean = self.preprocess_text(query)
            query_vec = self.vectorizer.transform([query_clean])
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

            # ترتيب النتائج حسب أعلى تشابه
            top_indices = similarities.argsort()[::-1][:top_n]
            best_score = similarities[top_indices[0]]

            if best_score == 0:
                return "⚠️ لم يتم العثور على تطابق مباشر في قاعدة البيانات.", "", ""

            row = self.db.iloc[top_indices[0]]
            answer = row.get('النص', 'لا يوجد نص متاح.')
            reference = f"المادة {row.get('المادة', 'غير محددة')} - القسم: {row.get('القسم', 'غير محدد')}"
            example = row.get('مثال', 'لا يوجد مثال متاح.')

            return answer, reference, example

        except Exception as e:
            return f"⚠️ حدث خطأ أثناء عملية البحث: {e}", "", ""