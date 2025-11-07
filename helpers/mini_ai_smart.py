import pandas as pd
import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
from datetime import datetime
import json

class MiniLegalAI:
    def __init__(self, workbook_path=None):
        """
        🤖 المساعد القانوني الذكي - الإصدار المحسن
        
        يعتمد على خوارزميات ML للبحث الذكي في التشريعات القانونية
        """
        # جلب الإعدادات
        config = st.session_state.get("config", {})
        self.ai_enabled = config.get("AI", {}).get("ENABLE", True)
        self.min_similarity_threshold = config.get("AI", {}).get("MIN_SIMILARITY", 0.1)
        
        if not self.ai_enabled:
            st.warning("🤖 المساعد الذكي معطل من إعدادات النظام.")
        
        # المسارات والإعدادات
        self.workbook_path = workbook_path or config.get("WORKBOOK_PATH", "")
        self.last_updated = None
        
        # تهيئة مكونات ML
        self.vectorizer = None
        self.tfidf_matrix = None
        self.feature_names = None
        
        # قاعدة البيانات الافتراضية
        self.db = pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال', 'التصنيف', 'الأهمية'])
        
        # إحصائيات الاستخدام
        self.search_history = []
        self.total_searches = 0
        
        # التحميل التلقائي إذا كان الملف موجوداً
        if self.workbook_path and os.path.exists(self.workbook_path):
            self.load_database_from_excel()
            if not self.db.empty:
                self.build_tfidf_matrix()

    # ==============================
    # 📊 تحميل قاعدة البيانات
    # ==============================
    def load_database_from_excel(self, path=None):
        """تحميل قاعدة البيانات من ملف Excel مع معالجة متقدمة للأخطاء"""
        path = path or self.workbook_path
        
        if not path or not os.path.exists(path):
            st.warning(f"⚠️ ملف قاعدة البيانات غير موجود: {path}")
            self.db = pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال', 'التصنيف', 'الأهمية'])
            return False
        
        try:
            # قراءة الملف مع معالجة مختلف الصيغ
            df = pd.read_excel(path, engine='openpyxl')
            
            # التأكد من وجود الأعمدة الأساسية
            required_columns = ['المادة', 'القسم', 'النص', 'مثال']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # إضافة أعمدة إضافية إذا لم تكن موجودة
            optional_columns = ['التصنيف', 'الأهمية', 'تاريخ_التحديث']
            for col in optional_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # تنظيف البيانات
            df = df[required_columns + optional_columns]
            df.fillna("", inplace=True)
            
            # إزالة الصفوف الفارغة
            df = df[df['النص'].str.strip() != ""]
            
            self.db = df
            self.last_updated = datetime.now()
            
            # حفظ في session state للوصول السريع
            st.session_state['ai_db'] = df
            st.session_state['db_loaded'] = True
            
            st.success(f"✅ تم تحميل {len(df)} سجل قانوني بنجاح")
            return True
            
        except Exception as e:
            st.error(f"❌ خطأ في تحميل قاعدة البيانات: {str(e)}")
            self.db = pd.DataFrame(columns=required_columns + optional_columns)
            return False

    # ==============================
    # 🧹 تنظيف النصوص المتقدم
    # ==============================
    @staticmethod
    def preprocess_text(text):
        """تنظيف وتحضير النص لمعالجة اللغة الطبيعية"""
        if pd.isna(text) or text == "":
            return ""
        
        text = str(text).strip()
        
        # إزالة الرموز الخاصة مع الحفاظ على الحروف العربية
        text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
        
        # تقليل المسافات المتعددة
        text = re.sub(r"\s+", " ", text)
        
        # تحويل إلى حروف صغيرة (للكلمات الإنجليزية فقط)
        text = text.lower()
        
        return text

    # ==============================
    # 🏗️ بناء مصفوفة TF-IDF المحسنة
    # ==============================
    def build_tfidf_matrix(self):
        """بناء مصفوفة TF-IDF للبحث الدلالي المتقدم"""
        if self.db.empty:
            st.warning("⚠️ لا يمكن بناء مصفوفة البحث - قاعدة البيانات فارغة")
            return False
        
        try:
            # تحضير النصوص
            corpus = self.db['النص'].apply(self.preprocess_text).tolist()
            
            # إعداد الـ Vectorizer مع إعدادات متقدمة للغة العربية
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                min_df=1,
                max_df=0.8,
                ngram_range=(1, 2),  # دعم للكلمات المركبة
                stop_words=None  # يمكن إضافة قائمة توقف للعربية لاحقاً
            )
            
            # بناء المصفوفة
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            self.feature_names = self.vectorizer.get_feature_names_out()
            
            st.success(f"🎯 تم بناء مصفوفة البحث بـ {len(self.feature_names)} ميزة لغوية")
            return True
            
        except Exception as e:
            st.error(f"❌ خطأ في بناء مصفوفة البحث: {str(e)}")
            return False

    # ==============================
    # 🔍 البحث الذكي المتقدم
    # ==============================
    def advanced_search(self, query, top_n=3, min_score=0.1):
        """
        بحث ذكي متقدم في التشريعات القانونية
        
        Args:
            query (str): استعلام البحث
            top_n (int): عدد النتائج المطلوبة
            min_score (float): الحد الأدنى لدقة المطابقة
            
        Returns:
            list: قائمة بالنتائج مع التفاصيل
        """
        # فحص الإعدادات الأساسية
        if not self.ai_enabled:
            return [{
                "text": "🤖 المساعد الذكي معطل حاليًا",
                "reference": "",
                "example": "",
                "score": 0,
                "article": "",
                "section": ""
            }]
        
        if self.db.empty or self.tfidf_matrix is None:
            return [{
                "text": "⚠️ قاعدة البيانات غير جاهزة للبحث",
                "reference": "",
                "example": "",
                "score": 0,
                "article": "",
                "section": ""
            }]
        
        # تسجيل البحث في السجل
        self.total_searches += 1
        self.search_history.append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results_count": 0
        })
        
        try:
            # تحضير الاستعلام
            processed_query = self.preprocess_text(query)
            if not processed_query.strip():
                return [{
                    "text": "⚠️ يرجى إدخال استبحث واضح",
                    "reference": "",
                    "example": "",
                    "score": 0,
                    "article": "",
                    "section": ""
                }]
            
            # تحويل الاستعلام إلى متجه
            query_vec = self.vectorizer.transform([processed_query])
            
            # حساب التشابه
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # الحصول على أفضل النتائج
            top_indices = similarities.argsort()[::-1][:top_n]
            
            results = []
            for idx in top_indices:
                score = similarities[idx]
                
                # تصفية النتائج ذات الدقة المنخفضة
                if score < min_score:
                    continue
                
                row = self.db.iloc[idx]
                result = {
                    "text": row.get("النص", ""),
                    "reference": f"المادة {row.get('المادة', '')} - القسم: {row.get('القسم', '')}",
                    "example": row.get("مثال", ""),
                    "score": round(score * 100, 2),
                    "article": row.get("المادة", ""),
                    "section": row.get("القسم", ""),
                    "category": row.get("التصنيف", ""),
                    "importance": row.get("الأهمية", "")
                }
                results.append(result)
            
            # تحديث سجل البحث
            if self.search_history:
                self.search_history[-1]["results_count"] = len(results)
            
            if not results:
                return [{
                    "text": "🔍 لم يتم العثور على نتائج تطابق استعلامك",
                    "reference": "جرب استخدام كلمات بحثية مختلفة",
                    "example": "",
                    "score": 0,
                    "article": "",
                    "section": ""
                }]
            
            return results
            
        except Exception as e:
            st.error(f"❌ خطأ في عملية البحث: {str(e)}")
            return [{
                "text": "⚠️ حدث خطأ في البحث، يرجى المحاولة لاحقاً",
                "reference": "",
                "example": "",
                "score": 0,
                "article": "",
                "section": ""
            }]

    # ==============================
    # 📈 إحصائيات وأدوات مساعدة
    # ==============================
    def get_statistics(self):
        """إرجاع إحصائيات استخدام المساعد"""
        return {
            "total_records": len(self.db),
            "total_searches": self.total_searches,
            "last_updated": self.last_updated,
            "ai_enabled": self.ai_enabled,
            "search_history": self.search_history[-10:]  # آخر 10 عمليات بحث
        }
    
    def search_similar_articles(self, article_text, top_n=2):
        """البحث عن مواد مشابهة لنص مادة معينة"""
        return self.advanced_search(article_text, top_n=top_n)
    
    def get_categories_stats(self):
        """إحصائيات التصنيفات الموجودة في القاعدة"""
        if self.db.empty or 'التصنيف' not in self.db.columns:
            return {}
        
        return self.db['التصنيف'].value_counts().to_dict()

    # ==============================
    # 🔄 إعادة التحميل والتحديث
    # ==============================
    def reload(self, new_path=None):
        """إعادة تحميل قاعدة البيانات وتحديث مصفوفة البحث"""
        if new_path:
            self.workbook_path = new_path
        
        success = self.load_database_from_excel()
        if success and not self.db.empty:
            self.build_tfidf_matrix()
            st.success("🔄 تم تحديث قاعدة البيانات ومصفوفة البحث بنجاح")
        else:
            st.warning("⚠️ لم يتم تحديث قاعدة البيانات")
        
        return success

    # ==============================
    # 💾 حفظ وتصدير البيانات
    # ==============================
    def export_search_history(self, format='json'):
        """تصدير سجل البحث"""
        if format == 'json':
            return json.dumps(self.search_history, ensure_ascii=False, indent=2)
        else:
            return pd.DataFrame(self.search_history).to_csv(index=False)

# دالة مساعدة للاستخدام السريع
def create_legal_ai(workbook_path=None):
    """إنشاء مثيل مساعد قانوني ذكي"""
    return MiniLegalAI(workbook_path)

# مثال للاستخدام
if __name__ == "__main__":
    # اختبار الوظائف
    ai = MiniLegalAI("data/legal_database.xlsx")
    results = ai.advanced_search("مكافأة نهاية الخدمة")
    print(results)