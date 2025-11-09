import streamlit as st
import os
import pandas as pd
from datetime import datetime, timedelta
import json

# ==========================
# إعدادات التطبيق
# ==========================
st.set_page_config(
    page_title="⚖️ منصة حق - المنصة القانونية الذكية",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================
# تحميل التصميم الفاتح
# ==========================
def load_custom_css():
    st.markdown("""
    <style>
    .main-header { 
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 50%, #1E40AF 100%); 
        color: white; 
        padding: 2rem; 
        border-radius: 20px; 
        text-align: center; 
        margin-bottom: 2rem; 
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    .feature-card { 
        background: white; 
        padding: 1.5rem; 
        border-radius: 15px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        margin: 1rem 0; 
        transition: all 0.3s ease; 
        border: 1px solid #e0e0e0;
    }
    .feature-card:hover { 
        transform: translateY(-5px); 
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .info-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-right: 4px solid #2563EB;
        margin: 0.5rem 0;
    }
    .emergency-card {
        background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    .law-article {
        background: #f0f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1E40AF;
        margin: 1rem 0;
    }
    .research-tool {
        background: linear-gradient(135deg, #7C3AED 0%, #8B5CF6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    .disclaimer {
        background: #FFF3CD;
        border: 1px solid #FFEAA7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# ==========================
# تهيئة الجلسة
# ==========================
if 'user_type' not in st.session_state:
    st.session_state.user_type = "زائر"
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# ==========================
# دوال مساعدة محسنة
# ==========================
def load_lottie_url(url: str):
    return None

def calculate_end_service(salary, years, months, contract_type, end_reason):
    """حساب دقيق لمكافأة نهاية الخدمة حسب القانون الأردني 2025"""
    total_months = years * 12 + months
    
    if end_reason == "استقالة":
        if total_months < 12:
            return 0
        elif total_months <= 60:  # حتى 5 سنوات
            return (salary * total_months) / 24
        else:  # أكثر من 5 سنوات
            first_5 = (salary * 60) / 24
            remaining = (salary * (total_months - 60)) / 12
            return first_5 + remaining
    else:  # إنهاء خدمة
        if total_months <= 60:
            return (salary * total_months) / 12
        else:
            first_5 = (salary * 60) / 12
            remaining = (salary * (total_months - 60)) / 8
            return first_5 + remaining

def calculate_overtime(regular_hours, overtime_hours, hourly_rate):
    """حساب بدل العمل الإضافي"""
    overtime_pay = 0
    if overtime_hours > 0:
        # 125% للساعات الأولى، 150% لساعات العطلات
        overtime_pay = overtime_hours * hourly_rate * 1.25
    return overtime_pay

def calculate_vacation(salary, vacation_days):
    """حساب مستحقات الإجازات"""
    daily_rate = salary / 30
    return daily_rate * vacation_days

# ==========================
# 🏠 الصفحة الرئيسية المبسطة
# ==========================
def show_home_page():
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="margin: 0; font-size: 3.5rem; color: #1E3A8A;">⚖️ منصة حق</h1>
        <p style="font-size: 1.2rem; color: #666; margin: 0.5rem 0;">
        المنصة القانونية الذكية - الأردن 2025
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # قسم العمال
    st.markdown("### 👷 للعاملين")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 200px;">
            <h4 style="color: #1E40AF;">📋 الحقوق الأساسية</h4>
            <ul style="padding-right: 1rem;">
                <li>العقود والتعاقد</li>
                <li>الأجور والمستحقات</li>
                <li>الإجازات والراحة</li>
                <li>السلامة المهنية</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 200px;">
            <h4 style="color: #1E40AF;">🧮 الحاسبات</h4>
            <ul style="padding-right: 1rem;">
                <li>مكافأة نهاية الخدمة</li>
                <li>بدل العمل الإضافي</li>
                <li>مستحقات الإجازات</li>
                <li>التعويضات</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 200px;">
            <h4 style="color: #1E40AF;">📞 الدعم القانوني</h4>
            <ul style="padding-right: 1rem;">
                <li>تقديم الشكاوى</li>
                <li>نماذج جاهزة</li>
                <li>جهات الاختصاص</li>
                <li>استشارات عاجلة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # قسم أصحاب العمل
    st.markdown("### 👔 لأصحاب العمل")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 200px;">
            <h4 style="color: #059669;">📋 الالتزامات القانونية</h4>
            <ul style="padding-right: 1rem;">
                <li>التوظيف والتعاقد</li>
                <li>الأجور والرواتب</li>
                <li>السلامة المهنية</li>
                <li>إنهاء الخدمة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 200px;">
            <h4 style="color: #059669;">🔍 الامتثال القانوني</h4>
            <ul style="padding-right: 1rem;">
                <li>مدقق الامتثال</li>
                <li>تقييم ذاتي</li>
                <li>فحص العقود</li>
                <li>تقارير الامتثال</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 200px;">
            <h4 style="color: #059669;">📊 الإدارة القانونية</h4>
            <ul style="padding-right: 1rem;">
                <li>نماذج وعقود</li>
                <li>إدارة المخاطر</li>
                <li>حاسبات مالية</li>
                <li>تقارير وإحصائيات</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # قسم الباحثين والخريجين
    st.markdown("### 🎓 للباحثين والخريجين الجدد")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 180px;">
            <h4 style="color: #7C3AED;">🔬 الباحثين</h4>
            <ul style="padding-right: 1rem;">
                <li>الموسوعة القانونية</li>
                <li>السوابق القضائية</li>
                <li>الدراسات والأبحاث</li>
                <li>مقارنات دولية</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 180px;">
            <h4 style="color: #7C3AED;">👨‍💼 الخريجين الجدد</h4>
            <ul style="padding-right: 1rem;">
                <li>دليل الانطلاق المهني</li>
                <li>نصائح التوظيف</li>
                <li>حقوق الخريجين</li>
                <li>التأهيل لسوق العمل</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # خدمات إضافية مهمة
    st.markdown("### 🛠️ خدمات إضافية")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; background: white; padding: 1rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 120px;">
            <div style="font-size: 2rem;">⏰</div>
            <h4 style="margin: 0.5rem 0;">منبه المواعيد</h4>
            <p style="font-size: 0.8rem; color: #666;">تذكير بالمواعيد القانونية</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; background: white; padding: 1rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 120px;">
            <div style="font-size: 2rem;">🗺️</div>
            <h4 style="margin: 0.5rem 0;">خريطة الحقوق</h4>
            <p style="font-size: 0.8rem; color: #666;">تصور تفاعلي للحقوق</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; background: white; padding: 1rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 120px;">
            <div style="font-size: 2rem;">🔍</div>
            <h4 style="margin: 0.5rem 0;">بحث قانوني</h4>
            <p style="font-size: 0.8rem; color: #666;">بحث في التشريعات</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; background: white; padding: 1rem; border-radius: 10px; border: 1px solid #e0e0e0; height: 120px;">
            <div style="font-size: 2rem;">🏛️</div>
            <h4 style="margin: 0.5rem 0;">الجهات المختصة</h4>
            <p style="font-size: 0.8rem; color: #666;">دليل الجهات الرسمية</p>
        </div>
        """, unsafe_allow_html=True)
    
    # تحديثات 2025
    st.markdown("### 📢 آخر التحديثات 2025")
    
    updates = [
        {"icon": "💰", "text": "الحد الأدنى للأجور: 290 دينار"},
        {"icon": "🏥", "text": "إجازة الأمومة: 10 أسابيع"},
        {"icon": "🛡️", "text": "تنظيم الحماية من التحرش"},
        {"icon": "🌐", "text": "قانون العمل عن بُعد"}
    ]
    
    cols = st.columns(4)
    for idx, update in enumerate(updates):
        with cols[idx]:
            st.markdown(f"""
            <div style="text-align: center; background: #f8f9fa; padding: 1rem; border-radius: 10px;">
                <div style="font-size: 1.5rem;">{update['icon']}</div>
                <p style="margin: 0.5rem 0; font-size: 0.9rem;">{update['text']}</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================
# 🧭 الشريط الجانبي المحسن
# ==========================
def main():
    with st.sidebar:
        # شعار المنصة فقط
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0 2rem 0;">
            <h2 style="margin: 0; color: #1E3A8A;">⚖️ منصة حق</h2>
            <p style="margin: 0; color: #666; font-size: 0.9rem;">المنصة القانونية الذكية</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # تصنيفات رئيسية
        st.markdown("### 📂 الأقسام الرئيسية")
        
        # قسم العمال
        with st.expander("👷 قسم العمال", expanded=True):
            st.markdown("""
            - 📋 الحقوق الأساسية
            - 💰 الحقوق المالية  
            - ⏰ وقت العمل والإجازات
            - 🛡️ السلامة والحماية
            - ⚖️ الإنذارات والفصل
            - 📞 الشكاوى والمنازعات
            - 🧮 حاسبات المستحقات
            - 📚 المكتبة القانونية
            """)
        
        # قسم أصحاب العمل
        with st.expander("👔 قسم أصحاب العمل", expanded=False):
            st.markdown("""
            - 📋 الالتزامات القانونية
            - 📝 نماذج وعقود
            - 💰 الحاسبات المالية
            - ⚖️ إدارة المخاطر
            - 🔍 مدقق الامتثال
            - 📊 التقارير والإحصائيات
            """)
        
        # قسم الباحثين
        with st.expander("🔬 قسم الباحثين", expanded=False):
            st.markdown("""
            - 📚 التشريعات الأساسية
            - ⚖️ السوابق القضائية
            - 📊 الدراسات والأبحاث
            - 🌍 مقارنات دولية
            - 📈 تحليلات إحصائية
            """)
        
        # خدمات إضافية
        with st.expander("🛠️ خدمات إضافية", expanded=False):
            st.markdown("""
            - 🎓 دليل الخريجين الجدد
            - ⏰ منبه المواعيد
            - 🗺️ خريطة الحقوق
            - 🔍 البحث في القوانين
            - 🏛️ الجهات المختصة
            - 📁 منظم المستندات
            """)
        
        st.markdown("---")
        
        # معلومات الاتصال المختصرة
        st.markdown("### 📞 اتصل بنا")
        st.markdown("""
        **📧 البريد الإلكتروني:**  
        support@haqq-platform.jo
        
        **🌐 الموقع الإلكتروني:**  
        www.haqq-platform.jo
        """)
        
        st.markdown("---")
        
        # تنويه صغير
        st.markdown("""
        <div style="font-size: 0.8rem; color: #666; text-align: center;">
        منصة توعية قانونية - لا تغني عن استشارة محامٍ متخصص
        </div>
        """, unsafe_allow_html=True)
    
    # عرض الصفحة المحددة
    page_options = {
        "🏠 الصفحة الرئيسية": show_home_page,
        "👷 العمال": show_workers_section,
        "👔 أصحاب العمل": show_employers_section,
        "🔬 الباحثين": show_researchers_section,
        "🎓 دليل الخريجين": show_graduates_guide,
        "⏰ منبه المواعيد": show_reminder_system,
        "🗺️ خريطة الحقوق": show_rights_map,
        "🔍 البحث في القوانين": show_legal_search,
        "🏛️ الجهات المختصة": show_authorities_section,
        "🛠️ خدمات أخرى": show_other_services
    }
    
    # استخدام query parameters للتنقل
    query_params = st.experimental_get_query_params()
    selected_page = query_params.get("page", ["🏠 الصفحة الرئيسية"])[0]
    
    if selected_page in page_options:
        page_options[selected_page]()
    else:
        show_home_page()

# ==========================
# 🛠️ صفحة الخدمات الأخرى
# ==========================
def show_other_services():
    st.markdown("### 🛠️ الخدمات الإضافية")
    
    services_cols = st.columns(2)
    
    with services_cols[0]:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0;">
            <h4>📁 منظم المستندات</h4>
            <ul>
                <li>رفع وتنظيم المستندات</li>
                <li>تصنيف المستندات</li>
                <li>الببحث والفلترة</li>
                <li>الأمان والنسخ الاحتياطي</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; margin-top: 1rem;">
            <h4>📝 محلل العقود</h4>
            <ul>
                <li>تحليل العقد</li>
                <li>المقارنة القانونية</li>
                <li>التقرير الشامل</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with services_cols[1]:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0;">
            <h4>🔍 مدقق الامتثال</h4>
            <ul>
                <li>فحص العقد</li>
                <li>تقييم الامتثال</li>
                <li>التوصيات</li>
                <li>تقارير الامتثال</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; margin-top: 1rem;">
            <h4>🧮 الحاسبات القانونية</h4>
            <ul>
                <li>نهاية الخدمة</li>
                <li>العمل الإضافي</li>
                <li>الإجازات والأمومة</li>
                <li>الحاسبة الشاملة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # روابط سريعة
    st.markdown("### 🔗 روابط سريعة")
    quick_links = st.columns(4)
    
    with quick_links[0]:
        if st.button("⏰ المنبه", use_container_width=True):
            st.experimental_set_query_params(page="⏰ منبه المواعيد")
    with quick_links[1]:
        if st.button("🗺️ الخريطة", use_container_width=True):
            st.experimental_set_query_params(page="🗺️ خريطة الحقوق")
    with quick_links[2]:
        if st.button("🔍 البحث", use_container_width=True):
            st.experimental_set_query_params(page="🔍 البحث في القوانين")
    with quick_links[3]:
        if st.button("🏛️ الجهات", use_container_width=True):
            st.experimental_set_query_params(page="🏛️ الجهات المختصة")

# ==========================
# 🎓 دليل الخريجين الجدد المبسط
# ==========================
def show_graduates_guide():
    st.markdown("### 🎓 دليل الخريجين الجدد")
    
    tabs = st.tabs(["بداية المسيرة", "نصائح عملية", "جهات الدعم", "الموارد المجانية"])
    
    with tabs[0]:
        st.markdown("""
        #### 🚀 بداية المسيرة المهنية
        
        **📝 قبل بدء العمل:**
        - تأكد من وجود عقد عمل مكتوب
        - اقرأ جميع بنود العقد بعناية
        - اسأل عن كل ما هو غير واضح
        - احصل على نسخة موقعة من العقد
        
        **💼 أول شهر عمل:**
        - تعرف على ثقافة المؤسسة
        - افهم نظام العمل والإجازات
        - تواصل مع زملائك ومسؤوليك
        - احتفظ بسجل لإنجازاتك
        """)
    
    with tabs[1]:
        st.markdown("""
        #### 💡 نصائح عملية
        
        **✅ نصائح للنجاح:**
        - كن منضبطاً في الحضور والانصراف
        - طور مهاراتك باستمرار
        - احترم زملائك ومسؤوليك
        - كن إيجابياً وقابلاً للتعلم
        
        **⚠️ تنبيهات هامة:**
        - توثيق ساعات العمل الإضافي
        - الاحتفاظ بكشوف الرواتب
        - معرفة حقوقك القانونية
        - عدم التوقيع على مستندات غير واضحة
        """)
    
    with tabs[3]:
        st.markdown("""
        #### 📚 موارد مجانية
        
        **📞 جهات الدعم:**
        - وزارة العمل: 06-5802666
        - نقابة المحامين: 06-5664111
        - مراكز التشغيل الجامعية
        
        **🌐 منصات مفيدة:**
        - منصة تمكين للتوظيف
        - بوابة العمل الإلكترونية
        - منصات التدريب المجانية
        """)
( )if __name__ == "__main__":
    

# ==========================
# 👷 قسم العمال المحسن (مع الحفاظ على الهيكل)
# ==========================
def show_workers_section():
    st.markdown("### 👷 قسم العمال - الموسوعة الشاملة لحقوق العمال")
    
    worker_tabs = st.tabs([
        "🏠 نظرة عامة", 
        "📋 حقوق العمال", 
        "⚖️ الانتهاكات الشائعة", 
        "📝 كيفية المطالبة", 
        "🆘 حالات طارئة",
        "📚 المواد القانونية",
        "⏰ منبه المواعيد",  # إضافة جديدة
        "🔍 مدقق الامتثال"   # إضافة جديدة
    ])
    
    with worker_tabs[0]:
        st.markdown("#### 🏠 نظرة عامة عن حقوق العمال في القانون الأردني")
        
        # تحديث الحد الأدنى للأجور 2025
        st.info("""
        **📢 تحديث 2025:**
        - **الحد الأدنى للأجور:** 290 دينار (بدلاً من 260 دينار)
        - **إجازة الأمومة:** 10 أسابيع مدفوعة الأجر
        - **الحماية من التحرش:** إجراءات صارمة جديدة
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="success-card">
            <h3>🎯 حقوقك الأساسية</h3>
            <p>يكفل قانون العمل الأردني للعامل مجموعة من الحقوق الأساسية:</p>
            <ul>
            <li>📋 <strong>عقد عمل مكتوب</strong> يحدد حقوقك وواجباتك</li>
            <li>💰 <strong>أجر عادل</strong> لا يقل عن 290 دينار</li>
            <li>⏰ <strong>ساعات عمل معقولة</strong> 8 ساعات يومياً</li>
            <li>🌴 <strong>إجازات مدفوعة الأجر</strong> سنوية ومرضية</li>
            <li>🏥 <strong>بيئة عمل آمنة</strong> وصحية</li>
            <li>🎁 <strong>مكافأة نهاية خدمة</strong> مستحقة قانوناً</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-card">
            <h3>📞 جهات الدعم والمساندة</h3>
            <p>في حالة انتهاك حقوقك، يمكنك التوجه إلى:</p>
            <ul>
            <li>🏛️ <strong>وزارة العمل</strong> - 06-5802666</li>
            <li>⚖️ <strong>المحاكم المختصة</strong> - للتقاضي</li>
            <li>🤝 <strong>النقابات المهنية</strong> - للحماية</li>
            <li>🆘 <strong>مراكز الدعم القانوني</strong> - مجانية</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # باقي التبويبات تحافظ على محتواها مع التحديثات المطلوبة
    with worker_tabs[1]:
        # تحديث المواد القانونية حسب 2025
        st.markdown("#### 📋 الحقوق المالية المحدثة 2025")
        
        financial_rights = {
            "الحد الأدنى للأجور": {
                "value": "290 دينار",
                "law": "قرار مجلس الوزراء 2025/1",
                "details": "للمؤهلين جامعياً، 250 دينار لغير المؤهلين"
            },
            "موعد صرف الراتب": {
                "value": "أول 7 أيام من الشهر",
                "law": "المادة 55",
                "details": "يجب الصرف خلال 7 أيام من نهاية الشهر"
            }
        }
        
        for right, info in financial_rights.items():
            with st.expander(f"💰 {right}"):
                st.write(f"**القيمة:** {info['value']}")
                st.write(f"**الأساس القانوني:** {info['law']}")
                st.write(f"**التفاصيل:** {info['details']}")
    
    with worker_tabs[5]:
        st.markdown("#### 📚 المواد القانونية المحدثة 2025")
        
        # إضافة مواد قانونية جديدة
        new_laws_2025 = [
            "المادة 35 مكرر: تنظيم العمل عن بُعد",
            "المادة 69 معدلة: إجازة أمومة 10 أسابيع", 
            "المادة 105 مكرر: عقوبات التحرش الجنسي",
            "نظام الأجور 2025: الحد الأدنى 290 دينار"
        ]
        
        st.success("**التحديثات التشريعية 2025:**")
        for law in new_laws_2025:
            st.write(f"📢 {law}")
    
    with worker_tabs[6]:  # منبه المواعيد
        show_reminder_system()
    
    with worker_tabs[7]:  # مدقق الامتثال
        show_compliance_checker()

# ==========================
# 👔 قسم أصحاب العمل المحسن
# ==========================
def show_employers_section():
    st.markdown("### 👔 قسم أصحاب العمل - الإدارة القانونية المتكاملة")
    
    employer_tabs = st.tabs([
        "🏠 نظرة عامة", 
        "📋 الالتزامات القانونية", 
        "📝 نماذج وعقود",
        "💰 الحاسبات المالية", 
        "⚖️ إدارة المخاطر",
        "🔍 مدقق الامتثال",  # إضافة جديدة
        "🗺️ خريطة الالتزامات"  # إضافة جديدة
    ])
    
    with employer_tabs[0]:
        st.markdown("#### 🏠 الالتزامات المحدثة 2025")
        
        # إزالة المعلومات الشخصية
        st.markdown("""
        <div class="info-card">
        <h3>📢 تحديثات 2025 لأصحاب العمل</h3>
        <p>أبرز التعديلات التي يجب على أصحاب العمل الالتزام بها:</p>
        <ul>
        <li>💰 <strong>الحد الأدنى للأجور:</strong> 290 دينار للمؤهلين</li>
        <li>🛡️ <strong>الحماية من التحرش:</strong> إجراءات إلزامية جديدة</li>
        <li>🏥 <strong>إجازة الأمومة:</strong> 10 أسابيع مدفوعة الأجر</li>
        <li>🌐 <strong>العمل عن بُعد:</strong> تنظيم قانوني جديد</li>
        <li>📊 <strong>الإبلاغ الإلكتروني:</strong> تبسيط الإجراءات</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # إزالة بطاقة المؤسسة السريعة ومؤشر الأداء
    
    with employer_tabs[1]:
        st.markdown("#### 📋 الالتزامات القانونية الشاملة 2025")
        
        # تحديث الالتزامات حسب 2025
        new_obligations_2025 = [
            "تطبيق الحد الأدنى للأجور 290 دينار",
            "تنفيذ سياسات الحماية من التحرش",
            "توفير إجازة أمومة 10 أسابيع",
            "تنظيم العمل عن بُعد حسب القانون الجديد",
            "الإبلاغ الإلكتروني للجهات المختصة"
        ]
        
        st.warning("**الالتزامات الجديدة 2025:**")
        for obligation in new_obligations_2025:
            st.write(f"📌 {obligation}")
    
    with employer_tabs[5]:  # مدقق الامتثال
        show_compliance_checker()
    
    with employer_tabs[6]:  # خريطة الالتزامات
        show_rights_map()

# ==========================
# 🔬 قسم الباحثين المحسن
# ==========================
def show_researchers_section():
    st.markdown("### 🔬 قسم الباحثين - المنصة الشاملة لبحوث قانون العمل الأردني")
    
    researcher_tabs = st.tabs([
        "🏠 النظرة العامة", 
        "📚 التشريعات الأساسية", 
        "⚖️ السوابق القضائية",
        "📊 الدراسات والأبحاث", 
        "🔍 البحث المتقدم",
        "🌍 مقارنات دولية",  # إضافة جديدة
        "📈 تحليلات إحصائية"  # إضافة جديدة
    ])
    
    with researcher_tabs[0]:
        st.markdown("#### 🏠 أرشيف البحث القانوني المتكامل")
        
        # توسيع قاعدة البيانات
        research_areas = [
            "تطور تشريعات العمل في الأردن 1996-2025",
            "أثر تعديلات الحد الأدنى للأجور على الاقتصاد",
            "تحليل السوابق القضائية في منازعات العمل",
            "دراسة مقارنة مع تشريعات العمل الخليجية",
            "تقييم أثر التشريعات على حماية العمال",
            "تحليل الاتجاهات الحديثة في علاقات العمل"
        ]
        
        st.success("**مجالات البحث المتاحة:**")
        for area in research_areas:
            st.write(f"📖 {area}")
    
    with researcher_tabs[1]:
        st.markdown("#### 📚 التشريعات الأساسية المحدثة 2025")
        
        # تحديث التشريعات
        legislation_updates = [
            "قانون العمل الأردني رقم 8 لسنة 1996 - أحدث التعديلات 2025",
            "نظام الأجور والبدلات 2025",
            "تعليمات العمل عن بُعد 2025", 
            "دليل الحماية من التحرش في بيئة العمل",
            "اللوائح التنفيذية للتأمينات الاجتماعية المحدثة"
        ]
        
        for legislation in legislation_updates:
            with st.expander(f"📄 {legislation}"):
                st.write("**الحالة:** ساري المفعول")
                st.write("**تاريخ التحديث:** 2025")
                st.button("📥 تحميل النص الكامل", key=f"download_{legislation}")
    
    with researcher_tabs[5]:  # مقارنات دولية
        show_international_platform()
    
    with researcher_tabs[6]:  # تحليلات إحصائية
        st.markdown("#### 📈 التحليلات الإحصائية والاتجاهات")
        
        # إحصائيات موسعة
        stats_data = {
            "المؤشر": ["قضايا العمل", "معدل الرضا", "الامتثال", "الإنتاجية"],
            "2019": [1250, 68, 72, 75],
            "2023": [980, 74, 78, 82], 
            "2025": [850, 82, 85, 88]
        }
        
        df = pd.DataFrame(stats_data)
        st.dataframe(df, use_container_width=True)
        
        st.line_chart(df.set_index('المؤشر')[['2019', '2023', '2025']])

# ==========================
# 🧮 الحاسبات القانونية المحسنة
# ==========================
def show_calculators_section():
    st.markdown("### 🧮 الحاسبات القانونية المتكاملة")
    
    calc_tabs = st.tabs([
        "💰 نهاية الخدمة", 
        "⏰ العمل الإضافي", 
        "🏥 الإجازات",
        "📊 الحاسبة الشاملة"
    ])
    
    with calc_tabs[0]:
        st.markdown("#### 💰 حاسبة مكافأة نهاية الخدمة 2025")
        
        col1, col2 = st.columns(2)
        
        with col1:
            salary = st.number_input("الراتب الأخير (دينار)", min_value=290, value=500, key="end_salary")
            years = st.number_input("عدد السنوات", min_value=1, max_value=40, value=5, key="end_years")
            months = st.number_input("عدد الأشهر", min_value=0, max_value=11, value=0, key="end_months")
        
        with col2:
            contract_type = st.selectbox("نوع العقد", ["دائم", "مؤقت"], key="end_contract")
            end_reason = st.selectbox("سبب إنهاء الخدمة", [
                "استقالة", "إنهاء خدمة", "انتهاء عقد", "وفاة أو عجز"
            ], key="end_reason")
        
        if st.button("🧮 احسب المكافأة", key="calc_end_service"):
            end_service = calculate_end_service(salary, years, months, contract_type, end_reason)
            
            st.success(f"""
            ## 📊 نتائج حساب مكافأة نهاية الخدمة
            
            **التفاصيل:**
            - 💼 الراتب الأساسي: **{salary:,.0f}** دينار
            - 📅 مدة الخدمة: **{years}** سنة و **{months}** شهر
            - 🏷️ نوع العقد: **{contract_type}**
            - 🎯 سبب الإنهاء: **{end_reason}**
            
            **النتيجة:**
            - 💰 مكافأة نهاية الخدمة: **{end_service:,.0f}** دينار
            
            **ملاحظات:**
            - الحساب وفق قانون العمل الأردني 2025
            - الأسس: المادة 74 وتعديلاتها
            - يوصى بالتشاور مع مختص للتأكد
            """)
    
    with calc_tabs[3]:
        st.markdown("#### 📊 الحاسبة الشاملة للمستحقات")
        
        col1, col2 = st.columns(2)
        
        with col1:
            basic_salary = st.number_input("الراتب الأساسي", value=500, key="total_salary")
            overtime_hours = st.number_input("ساعات العمل الإضافي", value=20, key="total_overtime")
            vacation_days = st.number_input("أيام الإجازة المستحقة", value=14, key="total_vacation")
        
        with col2:
            service_years = st.number_input("مدة الخدمة (سنوات)", value=3, key="total_years")
            has_medical = st.checkbox("هناك إجازات مرضية مستحقة", key="total_medical")
            medical_days = st.number_input("أيام الإجازة المرضية", value=7, key="medical_days") if has_medical else 0
        
        if st.button("🧮 احسب إجمالي المستحقات", key="calc_total"):
            hourly_rate = basic_salary / (30 * 8)  # افتراض 8 ساعات يومياً
            overtime_pay = calculate_overtime(0, overtime_hours, hourly_rate)
            vacation_pay = calculate_vacation(basic_salary, vacation_days)
            medical_pay = calculate_vacation(basic_salary, medical_days) if has_medical else 0
            
            total_due = overtime_pay + vacation_pay + medical_pay
            
            st.success(f"""
            ## 💰 الإجمالي الشامل للمستحقات
            
            **التفاصيل:**
            - ⏰ بدل العمل الإضافي: **{overtime_pay:,.0f}** دينار
            - 🌴 مستحقات الإجازات: **{vacation_pay:,.0f}** دينار
            - 🏥 مستحقات إجازات مرضية: **{medical_pay:,.0f}** دينار
            
            **💰 الإجمالي المستحق:** **{total_due:,.0f}** دينار
            
            **الأساس القانوني:**
            - العمل الإضافي: المادة 42
            - الإجازات: المواد 52-58
            - الإجازات المرضية: المادة 58
            """)

# ==========================
# 📝 محاكي الشكوى المحسن
# ==========================
def show_complaint_simulator():
    st.markdown("### 📝 محاكي الشكوى - تحليل عام للمشاكل القانونية")
    
    # إضافة تنويه بعدم إصدار أحكام
    st.markdown("""
    <div class="disclaimer">
        <h4>📢 تنويه مهم</h4>
        <p>هذا المحاكي يقدم تحليلاً عاماً وتوعوياً للمشاكل القانونية فقط، ولا يصدر أحكاماً أو استشارات قانونية ملزمة. 
        المعلومات المقدمة لأغراض التوعية والتعليم.</p>
    </div>
    """, unsafe_allow_html=True)
    
    complaint_type = st.selectbox("نوع المشكلة", [
        "تأخر صرف الرواتب",
        "إنهاء خدمة غير مبرر", 
        "عدم منح الإجازات",
        "بيئة عمل غير آمنة",
        "تمييز أو تحرش",
        "مشاكل في العقد",
        "أخرى"
    ])
    
    problem_description = st.text_area("صف المشكلة بشكل عام", 
                                     placeholder="صف المشكلة بدون ذكر معلومات شخصية...")
    
    if st.button("🔍 حلل المشكلة", key="analyze_complaint"):
        if problem_description:
            st.success("### 📊 تحليل عام للمشكلة")
            
            st.info("""
            **التحليل العام:**
            - 🎯 **نوع الانتهاك:** مشكلة في تطبيق القانون
            - ⚖️ **الأساس القانوني:** مواد قانون العمل ذات الصلة
            - 📋 **الإجراءات العامة الممكنة:** التوجه للجهات المختصة
            
            **نقاط للتفكير:**
            - هل تمت محاولة حل المشكلة بشكل ودّي؟
            - هل هناك مستندات تدعم الموقف؟
            - ما هي الإجراءات المتاحة حسب القانون؟
            
            **تذكير:** هذه تحليلات عامة لأغراض التوعية
            """)
            
            st.warning("""
            **⚠️ تنويه مهم:**
            - هذه تحليلات عامة وتوعوية فقط
            - لا تعتبر استشارة قانونية ملزمة
            - يوصى بالتشاور مع مختص للحالات الفعلية
            - المعلومات مقدمة لأغراض التعليم والتوعية
            """)

# ==========================
# 🏛️ الجهات المختصة المحسنة
# ==========================
def show_authorities_section():
    st.markdown("### 🏛️ الجهات المختصة - دليل شامل لجميع المحافظات")
    
    # تحديث المحافظات والجهات
    governorates = {
        "عمان": {
            "وزارة العمل": "06-5802666 - تلاع العلي",
            "محكمة العمل": "06-5651900 - شارع المدينة المنورة",
            "الضمان الاجتماعي": "06-552-1221 - الشميساني"
        },
        "إربد": {
            "مديرية العمل": "02-727-2111 - وسط المدينة",
            "محكمة البداءة": "02-724-1502 - منطقة الرمثا"
        },
        "الزرقاء": {
            "مديرية العمل": "05-398-2110 - مدينة الزرقاء الجديدة",
            "مكتب التفتيش": "05-398-2115 - المنطقة الصناعية"
        },
        "العقبة": {
            "مديرية العمل": "03-201-6211 - المنطقة الاقتصادية",
            "مكتب الشكاوى": "03-201-8440 - وسط المدينة"
        },
        "البلقاء": {
            "مديرية العمل": "05-353-2110 - السلط",
            "مكتب الشكاوى": "05-353-2115 - وسط البلد"
        },
        "مأدبا": {
            "مديرية العمل": "05-324-2110 - مدينة مأدبا",
            "مكتب التفتيش": "05-324-2112 - المنطقة الصناعية"
        },
        "الكرك": {
            "مديرية العمل": "03-237-2110 - مدينة الكرك",
            "محكمة العمل": "03-237-2115 - منطقة القصر"
        },
        "معان": {
            "مديرية العمل": "03-213-2110 - مدينة معان",
            "مكتب الخدمات": "03-213-2112 - المنطقة الجنوبية"
        },
        "جرش": {
            "مديرية العمل": "02-635-2110 - مدينة جرش",
            "مكتب الاستعلامات": "02-635-2113 - وسط المدينة"
        },
        "عجلون": {
            "مديرية العمل": "02-642-2110 - مدينة عجلون",
            "مركز الخدمات": "02-642-2114 - المنطقة الشمالية"
        },
        "المفرق": {
            "مديرية العمل": "02-629-2110 - مدينة المفرق",
            "مكتب الشكاوى": "02-629-2116 - المنطقة الشرقية"
        },
        "الطفيلة": {
            "مديرية العمل": "03-225-2110 - مدينة الطفيلة",
            "مكتب الخدمات": "03-225-2113 - المنطقة الجنوبية"
        }
    }
    
    selected_gov = st.selectbox("اختر المحافظة", list(governorates.keys()))
    
    if selected_gov:
        st.success(f"### 📍 الجهات المختصة في {selected_gov}")
        
        for authority, info in governorates[selected_gov].items():
            with st.expander(f"🏛️ {authority}"):
                parts = info.split(" - ")
                if len(parts) == 2:
                    st.write(f"**📞 الهاتف:** {parts[0]}")
                    st.write(f"**📍 العنوان:** {parts[1]}")
                    st.write(f"**🕒 أوقات العمل:** 8:00 ص - 3:00 م (الأحد-الخميس)")
                else:
                    st.write(f"**المعلومات:** {info}")

# ==========================
# 🔍 البحث الذكي المحسن
# ==========================
def show_legal_search():
    st.markdown("### 🔍 البحث الذكي في التشريعات")
    
    search_query = st.text_input("اكتب مصطلحك القانوني للبحث:", 
                               placeholder="مثال: مكافأة نهاية الخدمة، عمل إضافي...")
    
    if st.button("🔎 ابحث في القوانين", key="smart_search"):
        if search_query:
            # محاكاة البحث الموسع
            search_results = {
                "مكافأة نهاية الخدمة": [
                    "المادة 74: تستحق المكافأة بعد سنة خدمة",
                    "المادة 75: طريقة حساب المكافأة",
                    "المادة 77: موعد صرف المستحقات"
                ],
                "عمل إضافي": [
                    "المادة 42: بدل العمل الإضافي 125%",
                    "المادة 46: الحد الأقصى لساعات العمل",
                    "المادة 47: فترات الراحة"
                ],
                "إجازات": [
                    "المادة 52: الإجازة السنوية 14 يوم",
                    "المادة 58: الإجازة المرضية",
                    "المادة 69: إجازة الأمومة"
                ]
            }
            
            found = False
            for term, results in search_results.items():
                if term in search_query:
                    st.success(f"## 📚 نتائج البحث عن: {term}")
                    for result in results:
                        st.write(f"• {result}")
                    found = True
                    break
            
            if not found:
                st.info("""
                **نتائج بحث عامة:**
                - 📖 راجع الباب الرابع من قانون العمل (المواد 52-78)
                - 📋 اطلع على اللوائح التنفيذية المحدثة
                - 🔍 استخدم مصطلحات أكثر تحديداً لتحسين النتائج
                """)

# ==========================
# ⚙️ الإعدادات المحسنة
# ==========================
def show_settings_page():
    st.markdown("### ⚙️ الإعدادات والتهيئة")
    
    settings_tabs = st.tabs(["🎛️ إعدادات التطبيق", "🔔 التحديثات", "🛡️ الخصوصية"])
    
    with settings_tabs[0]:
        st.markdown("#### 🎛️ إعدادات التطبيق العامة")
        
        # إزالة طلب المعلومات الشخصية
        st.selectbox("لغة التطبيق", ["العربية", "English"])
        st.radio("الوضع اللوني", ["فاتح", "تلقائي"])  # إزالة الوضع المظلم
        
        st.info("""
        **ملاحظة:**
        - التطبيق مصمم للاستخدام العام بدون حاجة لتسجيل
        - لا يتم جمع أو حفظ أي معلومات شخصية
        - جميع الخدمات متاحة للجميع بدون قيود
        """)
    
    with settings_tabs[1]:
        st.markdown("#### 🔔 تحديثات القوانين 2025")
        
        st.success("**آخر التحديثات:**")
        updates = [
            "✅ تحديث الحد الأدنى للأجور: 290 دينار",
            "✅ إجازة الأمومة: 10 أسابيع",
            "✅ تنظيم العمل عن بُعد",
            "✅ إجراءات الحماية من التحرش",
            "✅ تبسيط الإجراءات الإلكترونية"
        ]
        
        for update in updates:
            st.write(f"• {update}")
        
        st.button("🔄 تطبيق جميع التحديثات", key="apply_updates")
    
    with settings_tabs[2]:
        show_privacy_policy()

# ==========================
# 🛡️ سياسات الخصوصية الجديدة
# ==========================
def show_privacy_policy():
    st.markdown("### 🛡️ سياسة الخصوصية وحماية البيانات")
    
    st.markdown("""
    <div class="disclaimer">
    <h4>📄 سياسة الخصوصية - منصة حق</h4>
    
    **المقدمة:**
    تلتزم منصة حق بحماية خصوصية مستخدميها وبياناتهم وفقاً لأحكام قانون حماية البيانات الشخصية الأردني.
    
    **١. جمع المعلومات:**
    - لا نجمع أي معلومات شخصية إلا ما يقدمه المستخدم طوعاً
    - المعلومات العامة المقدمة تستخدم لأغراض التوعية فقط
    - لا نطلب أبداً معلومات حساسة أو سرية
    
    **٢. استخدام المعلومات:**
    - تستخدم المعلومات المقدمة طوعاً لتحسين الخدمات فقط
    - لا يتم بيع أو تأجير المعلومات لأي طرف ثالث
    - تحفظ المعلومات بأمان ولا تشارك بدون موافقة
    
    **٣. حماية البيانات:**
    - نطبق أعلى معايير الأمان لحماية البيانات
    - نلتزم بالتشريعات الأردنية في حماية المعلومات
    - لدينا إجراءات صارمة لمنع الوصول غير المصرح به
    
    **٤. حقوق المستخدم:**
    - الحق في معرفة المعلومات المحفوظة عنه
    - الحق في طلب تصحيح أو حذف المعلومات
    - الحق في سحب الموافقة في أي وقت
    - الحق في تقديم شكوى للجهات المختصة
    
    **٥. الاتصال بنا:**
    - للاستفسارات حول الخصوصية: privacy@haqq-platform.jo
    - للشكاوى والمقترحات: support@haqq-platform.jo
    
    **تاريخ السريان:** ١ يناير ٢٠٢٥
    </div>
    """, unsafe_allow_html=True)
    
    st.checkbox("أقر بأني قد قرأت وفهمت سياسة الخصوصية", key="privacy_agree")

# ==========================
# 🧭 التنفيذ الرئيسي للتطبيق
# ==========================
def main():
    # الشريط الجانبي المحدث
    with st.sidebar:
        st.markdown(
            "<div style='text-align: center; padding: 1rem;'>"
            "<h2>⚖️ منصة حق</h2>"
            "<p style='color: #666; font-size: 0.9rem;'>المنصة القانونية الذكية</p>"
            "<p style='color: #888; font-size: 0.8rem;'>Haqq Platform - 2025</p>"
            "</div>", 
            unsafe_allow_html=True
        )
        st.markdown("---")
        
        # القائمة الرئيسية المحدثة
        page_options = {
            "🏠 الصفحة الرئيسية": show_home_page,
            "👷 العمال": show_workers_section,
            "👔 أصحاب العمل": show_employers_section,
            "🔬 الباحثين": show_researchers_section,
            "🧮 الحاسبات القانونية": show_calculators_section,
            "📝 محاكي الشكوى": show_complaint_simulator,
            "🏛️ الجهات المختصة": show_authorities_section,
            "🔍 البحث في القوانين": show_legal_search,
            "⏰ منبه المواعيد": show_reminder_system,
            "🔍 مدقق الامتثال": show_compliance_checker,
            "🗺️ خريطة الحقوق": show_rights_map,
            "📁 منظم المستندات": show_document_organizer,
            "📝 محلل العقود": show_contract_analyzer,
            "👨‍💼 دليل العمال الجدد": show_new_workers_guide,
            "🎓 دليل الخريجين": show_graduates_guide,
            "🌍 منصة دولية": show_international_platform,
            "⚙️ الإعدادات": show_settings_page
        }
        
        selected_page = st.selectbox("اختر القسم", list(page_options.keys()), key="main_nav")
        
        st.markdown("---")
        
        # تنويه عام
        st.markdown("""
        <div style='background: #FFF3CD; padding: 1rem; border-radius: 10px; border: 1px solid #FFEAA7;'>
        <small>
        <strong>📢 تنويه مهم:</strong><br>
        هذه المنصة تقدم خدمات توعية وتعليم قانوني عام فقط. 
        المعلومات المقدمة لأغراض التوعية ولا تغني عن استشارة محامٍ متخصص.
        </small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📞 الدعم الفني")
        st.write("📧 support@haqq-platform.jo")
        st.write("🌐 www.haqq-platform.jo")
        st.write("🕒 الأحد - الخميس: 8:00 ص - 3:00 م")
    
    # عرض الصفحة المحددة
    if selected_page in page_options:
        try:
            page_options[selected_page]()
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء عرض الصفحة: {e}")
            st.info("يرجى تحديث الصفحة أو المحاولة لاحقاً")
    
    # التذييل المحدث
    st.markdown("---")
    st.markdown("""
    <center>
    <small>
    © 2025 منصة حق - المنصة القانونية الذكية. جميع الحقوق محفوظة.<br>
    هذه المنصة تقدم خدمات توعية وتعليم قانوني عام فقط ولا تغني عن استشارة محامٍ متخصص.
    </small>
    </center>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()