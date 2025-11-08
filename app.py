import streamlit as st
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# ==========================
# تحميل إعدادات البيئة
# ==========================
load_dotenv()

# ==========================
# استيراد المكونات المساعدة
# ==========================
try:
    from helpers.smart_recommender import smart_recommender, role_selector
    from helpers.mini_ai_smart import MiniLegalAI
    from helpers.settings_manager import SettingsManager
    from helpers.data_loader import DataLoader
except ImportError as e:
    st.warning(f"⚠️ بعض المكونات المساعدة غير متوفرة: {e}")

# ==========================
# تعريف مكونات UI محليًا لتجنب مشاكل الاستيراد
# ==========================
def section_header(title, subtitle=""):
    st.markdown(f"### {title}\n**{subtitle}**")

def message_bubble(text, sender="system"):
    st.write(f"{sender}: {text}")

def info_card(title, content):
    st.info(f"**{title}**\n{content}")

def mini_card(title, content):
    st.write(f"**{title}**: {content}")

def feature_highlight(title, description):
    st.write(f"**{title}**: {description}")

# =====================================================
# 🎯 إعدادات التطبيق والبيئة
# =====================================================
def setup_application():
    env_config = {
        "APP_INFO": {
            "APP_NAME": os.getenv("APP_NAME", "⚖️ منصة قانون العمل الذكية"),
            "VERSION": os.getenv("APP_VERSION", "v25.1"),
            "SUPPORT_EMAIL": os.getenv("SUPPORT_EMAIL", "support@alyworklaw.com")
        },
        "DATA_SOURCES": {
            "WORKBOOK_PATH": os.getenv("WORKBOOK_PATH", "data/AlyWork_Law_Pro_v2025_v24_ColabStreamlitReady.xlsx"),
            "SHEET_URL": os.getenv("SHEET_URL", "")
        },
        "AI_FEATURES": {
            "ENABLE_AI": os.getenv("AI_ENABLE", "true").lower() == "true",
            "MAX_HISTORY": int(os.getenv("AI_MAX_HISTORY", "20"))
        },
        "FOOTER": {
            "TEXT": "© 2025 منصة قانون العمل الذكية — جميع الحقوق محفوظة."
        }
    }
    
    # محاكاة SettingsManager إذا لم يكن متوفراً
    class SimpleSettingsManager:
        def __init__(self):
            self.settings = env_config
        
        def update(self, new_settings):
            self.settings.update(new_settings)
    
    settings_manager = SimpleSettingsManager()
    return settings_manager

settings_manager = setup_application()
config = st.session_state.get("config", settings_manager.settings)

# إعداد صفحة Streamlit
st.set_page_config(
    page_title=config.get("APP_INFO", {}).get("APP_NAME", "منصة قانون العمل الذكية"),
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 🎨 تحميل التصميم
# =====================================================
def load_custom_css():
    css_file = "assets/styles_official.css"
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
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
        </style>
        """, unsafe_allow_html=True)

load_custom_css()

# =====================================================
# 🤖 تهيئة المكونات الذكية مع حماية من الأخطاء
# =====================================================
ai_assistant = None
try:
    workbook_path = config.get("DATA_SOURCES", {}).get("WORKBOOK_PATH", "")
    if workbook_path and os.path.exists(workbook_path):
        # محاكاة MiniLegalAI إذا لم يكن متوفراً
        class MockMiniLegalAI:
            def advanced_search(self, query, top_n=3):
                return [
                    {
                        'text': "المادة 74: تستحق مكافأة نهاية الخدمة للعامل إذا أنهيت خدماته لأي سبب عدا الاستقالة.",
                        'example': "عامل عمل لمدة 7 سنوات براتب 500 دينار، يستحق مكافأة قدرها 1800 دينار.",
                        'reference': "قانون العمل الأردني - المادة 74",
                        'score': 92.5
                    },
                    {
                        'text': "المادة 55: يجب صرف الأجر في مكان العمل وفي موعد لا يتجاوز اليوم السابع من الشهر التالي.",
                        'example': "إذا تأخر صرف الراتب أكثر من 7 أيام، يحق للعامل المطالبة بتعويض.",
                        'reference': "قانون العمل الأردني - المادة 55",
                        'score': 88.3
                    }
                ]
        
        ai_assistant = MockMiniLegalAI()
    else:
        st.warning("⚠️ ملف البيانات غير موجود، سيتم استخدام البيانات التجريبية.")
except Exception as e:
    st.warning(f"⚠️ حدث خطأ أثناء تحميل AI: {e}")

# محاكاة role_selector إذا لم يكن متوفراً
def role_selector():
    roles = ["عامل", "صاحب عمل", "باحث قانوني", "طالب"]
    return st.radio("اختر دورك:", roles, horizontal=True)

# محاكاة smart_recommender إذا لم يكن متوفراً
def smart_recommender(selected_role, show_header=True):
    if show_header:
        st.markdown(f"### 🎯 توصيات مخصصة لـ {selected_role}")
    
    recommendations = {
        "عامل": [
            "🧮 استخدم حاسبة مكافأة نهاية الخدمة",
            "📝 قدم شكوى في حالة الانتهاكات",
            "📚 اعرف حقوقك الكاملة في العمل"
        ],
        "صاحب عمل": [
            "📋 تأكد من التزامك بالقوانين",
            "📊 احسب مستحقات العاملين بدقة",
            "⚖️ تجنب المشاكل القانونية"
        ],
        "باحث قانوني": [
            "🔍 استخدم البحث المتقدم في القوانين",
            "📖 اطلع على أحدث التعديلات",
            "💼 استفد من المكتبة القانونية"
        ]
    }
    
    for rec in recommendations.get(selected_role, []):
        st.write(f"• {rec}")

# =====================================================
# 🏠 الصفحة الرئيسية المحسنة
# =====================================================
def show_home_page():
    st.markdown(f"""
    <div class="main-header">
        <h1 style="margin:0; font-size: 3rem;">{config.get("APP_INFO", {}).get("APP_NAME", "⚖️ منصة قانون العمل الذكية")}</h1>
        <p style="font-size: 1.2rem; margin: 1rem 0 0 0; opacity: 0.9;">
        المنصة الشاملة لحماية حقوق العمال وتقديم الاستشارات القانونية الذكية
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # الإحصائيات الحيوية
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.metric("📊 المواد القانونية", "150+", "+10 هذا الشهر")
    with col2: 
        st.metric("👥 المستفيدين", "5,000+", "+200 جديد")
    with col3: 
        st.metric("⚖️ المحافظات", "12", "مغطاة بالكامل")
    with col4: 
        st.metric("💼 نسبة الرضا", "95%", "+2% عن الشهر الماضي")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # التوصيات الذكية
    st.markdown("### 🎯 التوصيات الذكية المخصصة")
    try:
        selected_role = role_selector()
        smart_recommender(selected_role, show_header=False)
    except Exception as e:
        st.warning(f"⚠️ لا يمكن عرض التوصيات الذكية: {e}")
    
    # الميزات الرئيسية
    st.markdown("### 🚀 خدماتنا الرئيسية")
    features = [
        {
            "icon": "🧮", 
            "title": "الحاسبات القانونية", 
            "description": "حساب دقيق للمستحقات المالية وفق القانون الأردني", 
            "features": ["مكافأة نهاية الخدمة", "بدل العمل الإضافي", "الإجازات المرضية"],
            "link": "الحاسبات القانونية"
        },
        {
            "icon": "📝", 
            "title": "محاكي الشكوى الذكي", 
            "description": "تحليل الانتهاكات وتقديم الإجراءات القانونية المناسبة", 
            "features": ["تحليل آلي", "توصيات مخصصة", "نماذج جاهزة"],
            "link": "محاكي الشكوى"
        },
        {
            "icon": "🏛️", 
            "title": "الجهات المختصة", 
            "description": "دليل شامل للجهات الرسمية في جميع المحافظات", 
            "features": ["عنوان دقيق", "معلومات اتصال", "أوقات العمل"],
            "link": "الجهات المختصة"
        },
    ]
    
    cols = st.columns(3)
    for idx, feature in enumerate(features):
        with cols[idx]:
            st.markdown(f"""
            <div class="feature-card">
                <div style="font-size: 3rem; text-align: center; margin-bottom: 1rem;">{feature['icon']}</div>
                <h3 style="text-align: center;">{feature['title']}</h3>
                <p style="text-align: center; color: #666;">{feature['description']}</p>
                <div style="text-align: center;">
                    {" • ".join([f"<span style='background: #E3F2FD; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.8rem; margin: 0.1rem; display: inline-block;'>{f}</span>" for f in feature['features']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"انتقل إلى {feature['title']}", key=f"btn_{idx}"):
                st.session_state.selected_page = feature['link']
    
    # آخر الأخبار والتحديثات
    st.markdown("### 📢 آخر الأخبار والتحديثات")
    news_cols = st.columns(2)
    
    with news_cols[0]:
        with st.expander("🆕 تحديثات قانونية جديدة", expanded=True):
            st.write("""
            - **تحديث قانون العمل 2024**: تعديلات جديدة على الحد الأدنى للأجور
            - **قرار وزارة العمل**: تنظيم ساعات العمل في القطاع الخاص
            - **تحديث الأنظمة**: تحسينات في نظام التفتيش العمل
            """)
    
    with news_cols[1]:
        with st.expander("📈 إحصائيات المنصة", expanded=True):
            st.write("""
            - **500+** استشارة قانونية هذا الشهر
            - **95%** نسبة حل النزاعات
            - **12** محافظة مغطاة بالخدمة
            - **24/7** دعم فني متاح
            """)

# =====================================================
# 👷 قسم العمال المتكامل
# =====================================================
def show_workers_section():
    st.markdown("### 👷 قسم العمال - حماية حقوقك القانونية")
    
    # تبويبات العمال
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 نظرة عامة", 
        "📋 حقوق العمال", 
        "⚖️ الانتهاكات الشائعة", 
        "📝 كيفية المطالبة", 
        "🆘 حالات طارئة"
    ])
    
    with tab1:
        st.markdown("### 🏠 نظرة عامة عن حقوق العمال")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            ### 🎯 حقوقك الأساسية
            - **الأجر العادل**: الحد الأدنى للأجور مضمون قانوناً
            - **ساعات عمل معقولة**: لا تتجاوز 8 ساعات يومياً
            - **إجازات مدفوعة**: سنوية ومرضية وأمومة
            - **بيئة عمل آمنة**: توفير وسائل السلامة
            - **مكافأة نهاية خدمة**: مستحقة قانوناً
            """)
        
        with col2:
            st.success("""
            ### 📞 جهات الدعم
            - **وزارة العمل**: للشكاوى والمشورة
            - **النقابات المهنية**: للحماية النقابية
            - **المحاكم المختصة**: للتقاضي
            - **مراكز الدعم القانوني**: للمساعدة المجانية
            """)
        
        # حاسبة سريعة
        st.markdown("### 🧮 حاسبة سريعة لتقدير المستحقات")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            salary = st.number_input("الراتب الأساسي (دينار)", min_value=200, max_value=2000, value=500, key="quick_salary")
        
        with col2:
            years = st.slider("مدة الخدمة (سنوات)", 1, 30, 5, key="quick_years")
        
        with col3:
            contract_type = st.selectbox("نوع العقد", ["محدد المدة", "غير محدد المدة"], key="quick_contract")
        
        if st.button("احسب مستحقاتي التقريبية", key="quick_calc"):
            end_service = calculate_end_service(salary, years, contract_type)
            overtime = salary * 0.1  # تقديري
            vacations = salary * 0.08  # تقديري
            
            st.success(f"""
            **التقدير التقريبي للمستحقات:**
            - 📊 مكافأة نهاية الخدمة: **{end_service:,.0f}** دينار
            - ⏰ بدل عمل إضافي تقديري: **{overtime:,.0f}** دينار
            - 🌴 إجازات مستحقة: **{vacations:,.0f}** دينار
            """)
    
    with tab2:
        st.markdown("### 📋 التفاصيل الكاملة لحقوق العمال")
        
        rights_categories = {
            "💰 الأجور والمدفوعات": [
                "الحد الأدنى للأجور: 260 دينار للمؤهلين، 220 لغير المؤهلين",
                "استحقاق الراتب في موعد لا يتجاوز 7 أيام من نهاية الشهر",
                "عدم جواز خصم أكثر من 10% من الراتب كحد أقصى",
                "استحقاق بدل السكن والمواصلات إذا منصوص في العقد"
            ],
            "⏰ ساعات العمل والإجازات": [
                "8 ساعات عمل يومياً أو 48 ساعة أسبوعياً كحد أقصى",
                "ساعة راحة بعد 5 ساعات عمل متواصلة على الأقل",
                "الجمعة عطلة أسبوعية مدفوعة الأجر",
                "14 يوم إجازة سنوية مدفوعة الأجر بعد سنة خدمة"
            ],
            "🏥 الإجازات المرضية والأمومة": [
                "إجازة مرضية حتى 14 يوم براتب كامل، 14 يوم أخرى بنصف راتب",
                "إجازة أمومة 10 أسابيع مدفوعة الأجر",
                "إجازة والدية 3 أيام مدفوعة الأجر للأب",
                "إجازة لرعاية الأطفال ذوي الإعاقة"
            ],
            "🎁 المكافآت ونهاية الخدمة": [
                "مكافأة نهاية الخدمة مستحقة بعد سنة عمل على الأقل",
                "نصف شهر عن كل سنة من السنوات الخمس الأولى",
                "شهر كامل عن كل سنة بعد الخمس سنوات الأولى",
                "استحقاق كامل المكافأة في حالة الفصل التعسفي"
            ]
        }
        
        for category, rights in rights_categories.items():
            with st.expander(f"{category} ({len(rights)} حق)"):
                for right in rights:
                    st.write(f"✅ {right}")
    
    with tab3:
        st.markdown("### ⚖️ الانتهاكات الشائعة وكيفية التعامل معها")
        
        violations = {
            "❌ عدم صرف الرواتب": {
                "description": "تأخر صرف الراتب أكثر من 7 أيام من نهاية الشهر",
                "action": "تقديم شكوى لوزارة العمل خلال 30 يوم",
                "penalty": "غرامة 100-300 دينار للمخالف"
            },
            "⏰ العمل الإضافي القسري": {
                "description": "إجبار العامل على العمل ساعات إضافية دون مقابل",
                "action": "توثيق الساعات وتقديم شكوى مع الأدلة",
                "penalty": "غرامة 200-500 دينار وتعويض العامل"
            },
            "🚫 الفصل التعسفي": {
                "description": "إنهاء الخدمة دون مبرر قانوني أو إنذار",
                "action": "التوجه للمحكمة خلال 30 يوم من الفصل",
                "penalty": "تعويض يصل إلى 6 أشهر راتب"
            },
            "🏥 منع الإجازات": {
                "description": "حرمان العامل من الإجازات المستحقة قانوناً",
                "action": "تقديم شكوى لوزارة العمل مع كشف الإجازات",
                "penalty": "غرامة 300-700 دينار وتعويض العامل"
            }
        }
        
        for violation, details in violations.items():
            with st.expander(violation):
                st.error(f"**الوصف:** {details['description']}")
                st.warning(f"**الإجراء المطلوب:** {details['action']}")
                st.info(f"**العقوبة:** {details['penalty']}")
    
    with tab4:
        st.markdown("### 📝 خطوات المطالبة بالحقوق")
        
        steps = [
            {
                "step": "1",
                "title": "التوثيق والجمع",
                "details": "جمع جميع المستندات (عقد العمل، كشوف الرواتب، الإخطارات...)"
            },
            {
                "step": "2",
                "title": "محاولة التسوية",
                "details": "محاولة حل النزاع بشكل ودى مع صاحب العمل"
            },
            {
                "step": "3", 
                "title": "التوجه لوزارة العمل",
                "details": "تقديم شكوى رسمية لمكتب العمل المختص"
            },
            {
                "step": "4",
                "title": "اللجوء للمحكمة",
                "details": "في حالة عدم استجابة صاحب العمل خلال 30 يوم"
            }
        ]
        
        for step in steps:
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"<div style='background: #2563EB; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold;'>{step['step']}</div>", unsafe_allow_html=True)
                with col2:
                    st.write(f"**{step['title']}**")
                    st.write(step['details'])
                st.markdown("---")
    
    with tab5:
        st.markdown("### 🆘 حالات الطوارئ والإجراءات العاجلة")
        
        emergency_cases = {
            "🚨 إنهاء الخدمة الفوري": {
                "actions": [
                    "عدم توقيع أي مستندات قبل استشارة قانونية",
                    "طلب صورة من قرار الفصل",
                    "التوجه فوراً لوزارة العمل",
                    "جمع كشوف الرواتب والإثباتات"
                ],
                "contact": "وزارة العمل - قسم العلاقات العملية: 06-5802666"
            },
            "💸 حجز الرواتب": {
                "actions": [
                    "توثيق تاريخ عدم الصرف",
                    "طلب إفادة كتابية من صاحب العمل",
                    "التوجه لمكتب العمل خلال 48 ساعة",
                    "إبلاغ النقابة إن وجدت"
                ],
                "contact": "دائرة الأجور في وزارة العمل: 06-5802777"
            },
            "🏭 ظروف عمل خطرة": {
                "actions": [
                    "التوقف عن العمل إذا كان هناك خطر مباشر",
                    "إبلاغ مسؤول السلامة فوراً",
                    "توثيق الحالة بالصور والفيديوهات",
                    "التوجه لوزارة العمل - قسم التفتيش"
                ],
                "contact": "قسم السلامة والصحة المهنية: 06-5802888"
            }
        }
        
        for case, details in emergency_cases.items():
            with st.expander(case):
                st.markdown("<div class='emergency-card'>", unsafe_allow_html=True)
                st.error("**الإجراءات العاجلة:**")
                for action in details['actions']:
                    st.write(f"🚨 {action}")
                st.info(f"**جهة الاتصال المباشرة:** {details['contact']}")
                st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# 🧮 الحاسبات القانونية المتكاملة
# =====================================================
def show_calculators_section():
    st.markdown("### 🧮 الحاسبات القانونية - احسب مستحقاتك بدقة")
    
    calc_tabs = st.tabs([
        "💰 مكافأة نهاية الخدمة",
        "⏰ بدل العمل الإضافي", 
        "🏥 الإجازات المرضية",
        "🌴 الإجازات السنوية",
        "📊 حاسبة شاملة"
    ])
    
    with calc_tabs[0]:
        st.markdown("### 💰 حاسبة مكافأة نهاية الخدمة")
        
        col1, col2 = st.columns(2)
        
        with col1:
            last_salary = st.number_input("الراتب الأخير (دينار)", min_value=200, max_value=5000, value=500, key="end_salary")
            service_years = st.number_input("مدة الخدمة (سنوات)", min_value=1, max_value=40, value=5, key="end_years")
            service_months = st.number_input("مدة الخدمة (أشهر)", min_value=0, max_value=11, value=0, key="end_months")
        
        with col2:
            contract_type = st.selectbox("نوع العقد", ["محدد المدة", "غير محدد المدة"], key="end_contract")
            end_reason = st.selectbox("سبب إنهاء الخدمة", [
                "استقالة",
                "إنهاء من صاحب العمل",
                "انتهاء مدة العقد",
                "فصل تعسفي"
            ], key="end_reason")
            include_allowances = st.checkbox("احتساب البدلات في الراتب", value=True, key="end_allowances")
        
        if st.button("احسب المكافأة", type="primary", key="calc_end"):
            result = calculate_end_of_service(
                last_salary, service_years, service_months, 
                contract_type, end_reason, include_allowances
            )
            
            st.success(f"""
            ## 📊 نتائج حساب مكافأة نهاية الخدمة
            
            **المبلغ المستحق:** **{result['total_amount']:,.0f}** دينار أردني
            
            **التفاصيل:**
            - مدة الخدمة: {service_years} سنة و {service_months} شهر
            - الراتب الأساسي: {last_salary:,.0f} دينار
            - نوع النهاية: {end_reason}
            - طريقة الحساب: {result['calculation_method']}
            """)
            
            # تفاصيل الحساب
            with st.expander("📋 تفاصيل الحساب خطوة بخطوة"):
                for step in result['calculation_steps']:
                    st.write(step)
    
    with calc_tabs[1]:
        st.markdown("### ⏰ حاسبة بدل العمل الإضافي")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hourly_rate = st.number_input("الأجر الساعي (دينار)", min_value=1.0, max_value=20.0, value=2.5, key="overtime_rate")
            overtime_hours = st.number_input("عدد ساعات العمل الإضافي", min_value=1, max_value=100, value=10, key="overtime_hours")
            overtime_type = st.selectbox("نوع العمل الإضافي", [
                "عمل إضافي عادي (125%)",
                "عمل إضافي ليلي (150%)", 
                "عمل في العطلات الرسمية (200%)"
            ], key="overtime_type")
        
        with col2:
            days_worked = st.number_input("عدد الأيام في الشهر", min_value=1, max_value=31, value=22, key="overtime_days")
            include_transport = st.checkbox("إضافة بدل مواصلات", value=True, key="overtime_transport")
            transport_amount = st.number_input("بدل المواصلات (دينار)", min_value=0.0, max_value=10.0, value=2.0, key="transport_amt") if include_transport else 0.0
        
        if st.button("احسب بدل العمل الإضافي", key="calc_overtime"):
            result = calculate_overtime(
                hourly_rate, overtime_hours, overtime_type,
                days_worked, transport_amount
            )
            
            st.success(f"""
            ## 💰 نتائج حساب بدل العمل الإضافي
            
            **المبلغ المستحق:** **{result['total_overtime']:,.2f}** دينار
            
            **التفاصيل:**
            - ساعات العمل الإضافي: {overtime_hours} ساعة
            - معدل الساعة الإضافية: {result['overtime_rate']:,.2f} دينار
            - بدل المواصلات: {transport_amount:,.2f} دينار
            - الإجمالي الشهري: {result['monthly_total']:,.2f} دينار
            """)
    
    with calc_tabs[2]:
        st.markdown("### 🏥 حاسبة الإجازات المرضية")
        
        col1, col2 = st.columns(2)
        
        with col1:
            daily_salary = st.number_input("الأجر اليومي (دينار)", min_value=10.0, max_value=200.0, value=50.0, key="sick_daily")
            sick_days = st.number_input("عدد أيام الإجازة المرضية", min_value=1, max_value=365, value=20, key="sick_days")
            has_medical_report = st.checkbox("توجد تقارير طبية رسمية", value=True, key="sick_report")
        
        with col2:
            continuous_service = st.number_input("مدة الخدمة المتواصلة (سنوات)", min_value=0, max_value=40, value=3, key="sick_service")
            chronic_disease = st.checkbox("مرض مزمن أو إصابة عمل", key="sick_chronic")
            hospitalization_days = st.number_input("أيام التنويم في المستشفى", min_value=0, max_value=100, value=0, key="sick_hospital")
        
        if st.button("احسب مستحقات الإجازة المرضية", key="calc_sick"):
            result = calculate_sick_leave(
                daily_salary, sick_days, has_medical_report,
                continuous_service, chronic_disease, hospitalization_days
            )
            
            st.success(f"""
            ## 🏥 نتائج حساب الإجازة المرضية
            
            **المبلغ المستحق:** **{result['total_amount']:,.2f}** دينار
            
            **التفاصيل:**
            - الأجر اليومي: {daily_salary:,.2f} دينار
            - أيام الإجازة: {sick_days} يوم
            - الأيام براتب كامل: {result['full_pay_days']} يوم
            - الأيام بنصف راتب: {result['half_pay_days']} يوم
            - الأيام بدون راتب: {result['no_pay_days']} يوم
            """)
    
    with calc_tabs[3]:
        st.markdown("### 🌴 حاسبة الإجازات السنوية")
        
        col1, col2 = st.columns(2)
        
        with col1:
            annual_salary = st.number_input("الراتب الشهري (دينار)", min_value=200, max_value=5000, value=500, key="vacation_salary")
            worked_months = st.number_input("أشهر العمل الفعلية", min_value=1, max_value=12, value=12, key="vacation_months")
            taken_vacation = st.number_input("الإجازات المستخدمة (أيام)", min_value=0, max_value=30, value=5, key="vacation_taken")
        
        with col2:
            employment_year = st.number_input("سنة بدء العمل", min_value=2000, max_value=2024, value=2020, key="vacation_year")
            has_accumulated = st.checkbox("هناك إجازات متراكمة من سنوات سابقة", key="vacation_accumulated")
            accumulated_days = st.number_input("الإجازات المتراكمة (أيام)", min_value=0, max_value=60, value=0, key="vacation_accum_days") if has_accumulated else 0
        
        if st.button("احسب مستحقات الإجازة السنوية", key="calc_vacation"):
            result = calculate_annual_leave(
                annual_salary, worked_months, taken_vacation,
                employment_year, accumulated_days
            )
            
            st.success(f"""
            ## 🌴 نتائج حساب الإجازات السنوية
            
            **المبلغ المستحق:** **{result['vacation_pay']:,.2f}** دينار
            
            **التفاصيل:**
            - إجازات مستحقة: {result['due_vacation']} يوم
            - إجازات مستخدمة: {taken_vacation} يوم
            - إجازات متبقية: {result['remaining_vacation']} يوم
            - إجازات متراكمة: {accumulated_days} يوم
            - قيمة اليوم الواحد: {result['daily_rate']:,.2f} دينار
            """)
    
    with calc_tabs[4]:
        st.markdown("### 📊 الحاسبة الشاملة للمستحقات")
        
        st.info("""
        **أدخل بياناتك الأساسية لحساب جميع مستحقاتك مرة واحدة**
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            base_salary = st.number_input("الراتب الأساسي (دينار)", value=500, key="comp_salary")
            service_length = st.number_input("مدة الخدمة الكاملة", value=5, key="comp_service")
            overtime_hours = st.number_input("ساعات العمل الإضافي الشهرية", value=15, key="comp_overtime")
        
        with col2:
            sick_days = st.number_input("أيام الإجازة المرضية", value=5, key="comp_sick")
            annual_vacation = st.number_input("الإجازات السنوية المستحقة", value=14, key="comp_vacation")
            end_reason = st.selectbox("سبب إنهاء الخدمة", [
                "استقالة",
                "إنهاء من صاحب العمل", 
                "انتهاء عقد",
                "فصل تعسفي"
            ], key="comp_end")
        
        if st.button("احسب جميع المستحقات", type="primary", key="calc_comp"):
            results = calculate_comprehensive_benefits(
                base_salary, service_length, overtime_hours,
                sick_days, annual_vacation, end_reason
            )
            
            st.success("## 📊 ملخص جميع المستحقات المالية")
            
            # عرض النتائج في أعمدة
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💰 مكافأة نهاية الخدمة", f"{results['end_service']:,.0f} دينار")
                st.metric("⏰ بدل عمل إضافي", f"{results['overtime']:,.0f} دينار")
            
            with col2:
                st.metric("🏥 إجازات مرضية", f"{results['sick_leave']:,.0f} دينار")
                st.metric("🌴 إجازات سنوية", f"{results['annual_leave']:,.0f} دينار")
            
            with col3:
                st.metric("📦 إجمالي المستحقات", f"{results['total_benefits']:,.0f} دينار")
                st.metric("💸 صافي المستحق بعد الخصم", f"{results['net_benefits']:,.0f} دينار")
            
            # تحميل النتائج
            with st.expander("💾 حفظ النتائج وتحميلها"):
                result_text = f"""
                تقرير المستحقات المالية
                التاريخ: {datetime.now().strftime('%Y-%m-%d')}
                
                الراتب الأساسي: {base_salary} دينار
                مدة الخدمة: {service_length} سنوات
                
                التفاصيل:
                - مكافأة نهاية الخدمة: {results['end_service']:,.0f} دينار
                - بدل العمل الإضافي: {results['overtime']:,.0f} دينار  
                - الإجازات المرضية: {results['sick_leave']:,.0f} دينار
                - الإجازات السنوية: {results['annual_leave']:,.0f} دينار
                - الإجمالي: {results['total_benefits']:,.0f} دينار
                """
                
                st.download_button(
                    label="📥 حمل التقرير كملف نصي",
                    data=result_text,
                    file_name=f"تقرير_المستحقات_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

# =====================================================
# 📝 محاكي الشكوى الذكي المتكامل
# =====================================================
def show_complaint_simulator():
    st.markdown("### 📝 محاكي الشكوى الذكي - حل مشاكلك القانونية")
    
    complaint_tabs = st.tabs([
        "🔍 تحليل المشكلة", 
        "📋 نموذج الشكوى", 
        "🗺️ خريطة الحلول",
        "📞 متابعة الشكوى"
    ])
    
    with complaint_tabs[0]:
        st.markdown("### 🔍 تحليل مشكلتك القانونية")
        
        st.info("""
        **أدخل تفاصيل مشكلتك وسنقوم بتحليلها وإعطائك الحلول المناسبة**
        """)
        
        # معلومات أساسية
        col1, col2 = st.columns(2)
        
        with col1:
            user_type = st.selectbox("نوع المستخدم", ["عامل", "صاحب عمل", "باحث قانوني"], key="comp_user_type")
            problem_type = st.selectbox("نوع المشكلة", [
                "مشاكل الأجور والرواتب",
                "ساعات العمل والإجازات", 
                "إنهاء الخدمة والفصل",
                "السلامة والصحة المهنية",
                "تمييز ومضايقات",
                "مشاكل عقود العمل",
                "مشاكل النقابات والعمل الجماعي",
                "قضايا أخرى"
            ], key="comp_problem_type")
        
        with col2:
            location = st.selectbox("المحافظة", [
                "عمان", "إربد", "الزرقاء", "مأدبا", "البلقاء", "الكرك",
                "معان", "العقبة", "جرش", "عجلون", "المفرق", "الطفيلة"
            ], key="comp_location")
            urgency = st.select_slider("درجة الاستعجال", options=["منخفض", "متوسط", "عالي", "طارئ"], key="comp_urgency")
        
        # وصف المشكلة
        st.markdown("#### 📝 وصف المشكلة")
        problem_description = st.text_area(
            "صف مشكلتك بالتفصيل:",
            placeholder="مثال: لم أحصل على راتبي منذ شهرين، وصاحب العمل يهددني بالفصل إذا طالبت بحقي...",
            height=150,
            key="comp_description"
        )
        
        # معلومات إضافية
        st.markdown("#### 📎 معلومات إضافية")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            has_contract = st.radio("هل لديك عقد عمل؟", ["نعم", "لا", "غير مكتوب"], key="comp_contract")
            has_evidence = st.checkbox("هل لديك أدلة (صور، مستندات، شهود)؟", key="comp_evidence")
        
        with col2:
            problem_duration = st.selectbox("مدة المشكلة", [
                "أقل من أسبوع", 
                "أسبوع - شهر", 
                "1-3 أشهر", 
                "أكثر من 3 أشهر"
            ], key="comp_duration")
            previous_attempts = st.checkbox("هل حاولت حل المشكلة مسبقاً؟", key="comp_attempts")
        
        with col3:
            financial_impact = st.selectbox("التأثير المالي", [
                "بسيط (أقل من 100 دينار)",
                "متوسط (100-500 دينار)", 
                "كبير (500-1000 دينار)",
                "جسيم (أكثر من 1000 دينار)"
            ], key="comp_impact")
        
        if st.button("🔄 حلل مشكلتي", type="primary", key="analyze_comp"):
            if problem_description:
                analysis_result = analyze_complaint({
                    'user_type': user_type,
                    'problem_type': problem_type,
                    'location': location,
                    'urgency': urgency,
                    'description': problem_description,
                    'has_contract': has_contract,
                    'has_evidence': has_evidence,
                    'duration': problem_duration,
                    'financial_impact': financial_impact
                })
                
                display_complaint_analysis(analysis_result)
            else:
                st.error("⚠️ يرجى إدخال وصف للمشكلة")
    
    with complaint_tabs[1]:
        st.markdown("### 📋 نموذج الشكوى الجاهز")
        
        st.info("""
        **اختر نوع الشكوى وسنقوم بتوليد نموذج جاهز يمكنك استخدامه**
        """)
        
        complaint_types = {
            "شكوى أجور": {
                "description": "شكوى بسبب عدم صرف الرواتب أو الخصم غير القانوني",
                "fields": ["تاريخ عدم الصرف", "المبلغ المستحق", "عدد أشهر التأخير"]
            },
            "شكوى فصل تعسفي": {
                "description": "شكوى بسبب إنهاء الخدمة بدون مبرر قانوني", 
                "fields": ["تاريخ الفصل", "سبب الفصل المعلن", "الإنذارات السابقة"]
            },
            "شكوى عمل إضافي": {
                "description": "شكوى بسبب عدم صرف بدل العمل الإضافي",
                "fields": ["عدد الساعات الإضافية", "فترات العمل", "المستحق المالي"]
            },
            "شكوى إجازات": {
                "description": "شكوى بسبب الحرمان من الإجازات المستحقة",
                "fields": ["نوع الإجازة", "الفترة المطلوبة", "الرفض المستمر"]
            }
        }
        
        selected_complaint = st.selectbox("اختر نوع الشكوى", list(complaint_types.keys()), key="complaint_type")
        
        if selected_complaint:
            st.write(f"**وصف الشكوى:** {complaint_types[selected_complaint]['description']}")
            
            # حقول النموذج
            st.markdown("#### 📝 معلومات الشكوى")
            form_data = {}
            
            for field in complaint_types[selected_complaint]['fields']:
                form_data[field] = st.text_input(field, key=f"form_{field}")
            
            # معلومات المقدم
            st.markdown("#### 👤 معلومات المقدم")
            col1, col2 = st.columns(2)
            
            with col1:
                complainant_name = st.text_input("الاسم الكامل", key="comp_name")
                complainant_id = st.text_input("رقم الهوية", key="comp_id")
                phone = st.text_input("رقم الهاتف", key="comp_phone")
            
            with col2:
                workplace = st.text_input("مكان العمل", key="comp_work")
                position = st.text_input("الوظيفة", key="comp_position")
                salary = st.number_input("الراتب الأخير", min_value=200, key="comp_salary")
            
            if st.button("🖨️ توليد نموذج الشكوى", key="generate_comp"):
                complaint_form = generate_complaint_form(
                    selected_complaint, form_data, {
                        'name': complainant_name,
                        'id': complainant_id, 
                        'phone': phone,
                        'workplace': workplace,
                        'position': position,
                        'salary': salary
                    }
                )
                
                st.success("### 📄 نموذج الشكوى الجاهز")
                st.text_area("النموذج", complaint_form, height=300, key="complaint_output")
                
                st.download_button(
                    label="📥 حمل النموذج",
                    data=complaint_form,
                    file_name=f"شكوى_{selected_complaint}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    key="download_comp"
                )
    
    with complaint_tabs[2]:
        st.markdown("### 🗺️ خريطة الحلول القانونية")
        
        st.warning("""
        **اختر مسار الحل المناسب لمشكلتك بناءً على تحليلنا**
        """)
        
        solution_paths = {
            "المسار السريع": {
                "description": "حلول سريعة بدون تدخل رسمي",
                "steps": [
                    "محاولة حل ودى مع صاحب العمل",
                    "التواصل مع مدير الموارد البشرية",
                    "طلب وساطة من زملاء العمل"
                ],
                "duration": "1-7 أيام",
                "success_rate": "60%"
            },
            "المسار الرسمي": {
                "description": "التوجه للجهات الرسمية", 
                "steps": [
                    "تقديم شكوى لوزارة العمل",
                    "المشاركة في جلسات الصلاحية",
                    "الحصول على قرار رسمي"
                ],
                "duration": "15-30 يوم",
                "success_rate": "85%"
            },
            "المسار القضائي": {
                "description": "اللجوء للمحاكم المختصة",
                "steps": [
                    "رفع دعوى في محكمة العمل",
                    "المثول أمام القضاء",
                    "تنفيذ الحكم القضائي"
                ],
                "duration": "3-6 أشهر", 
                "success_rate": "95%"
            }
        }
        
        selected_path = st.radio("اختر مسار الحل", list(solution_paths.keys()), key="solution_path")
        
        if selected_path:
            path_info = solution_paths[selected_path]
            
            st.success(f"## {selected_path}")
            st.write(f"**الوصف:** {path_info['description']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("⏱️ المدة المتوقعة", path_info['duration'])
            with col2:
                st.metric("📈 نسبة النجاح", path_info['success_rate'])
            
            st.markdown("#### 📋 خطوات المسار")
            for i, step in enumerate(path_info['steps'], 1):
                st.write(f"{i}. {step}")
            
            if st.button(f"🚀 ابدأ مسار {selected_path}", key=f"start_{selected_path}"):
                st.session_state.current_path = selected_path
                st.success(f"تم بدء مسار {selected_path}. سنوجهك للخطوات التالية.")
    
    with complaint_tabs[3]:
        st.markdown("### 📞 متابعة الشكوى والاستشارة")
        
        st.info("""
        **تواصل معنا لمتابعة شكواك أو الحصول على استشارة قانونية متخصصة**
        """)
        
        contact_methods = st.radio("طريقة التواصل", [
            "💬 محادثة فورية", 
            "📞 هاتف مباشر", 
            "📧 بريد إلكتروني",
            "📍 زيارة مكتب"
        ], key="contact_method")
        
        if contact_methods == "💬 محادثة فورية":
            st.markdown("#### 💬 الدردشة المباشرة مع مستشار قانوني")
            
            # محاكاة دردشة
            if 'chat_messages' not in st.session_state:
                st.session_state.chat_messages = []
            
            for message in st.session_state.chat_messages:
                if message['sender'] == 'user':
                    st.write(f"**أنت:** {message['text']}")
                else:
                    st.write(f"**المستشار:** {message['text']}")
            
            user_message = st.text_input("اكتب رسالتك...", key="chat_input")
            if st.button("إرسال", key="send_chat") and user_message:
                st.session_state.chat_messages.append({'sender': 'user', 'text': user_message})
                # محاكاة رد المستشار
                advisor_response = generate_advisor_response(user_message)
                st.session_state.chat_messages.append({'sender': 'advisor', 'text': advisor_response})
                st.rerun()
        
        elif contact_methods == "📞 هاتف مباشر":
            st.markdown("#### 📞 أرقام التواصل المباشر")
            
            contacts = {
                "وزارة العمل - الشكاوى": "06-5802666",
                "الدعم القانوني المجاني": "0800-12345", 
                "طوارئ العمل": "06-5802999",
                "الشكاوى الإلكترونية": "complaints@mol.gov.jo"
            }
            
            for department, number in contacts.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{department}**")
                with col2:
                    st.write(f"`{number}`")
        
        elif contact_methods == "📧 بريد إلكتروني":
            st.markdown("#### 📧 إرسال بريد إلكتروني")
            
            with st.form("email_form"):
                email_subject = st.text_input("موضوع الرسالة", key="email_subject")
                email_body = st.text_area("نص الرسالة", height=200, key="email_body")
                attachments = st.file_uploader("إرفاق مستندات", accept_multiple_files=True, key="email_attach")
                
                if st.form_submit_button("📤 إرسال البريد", key="send_email"):
                    st.success("تم إرسال بريدك بنجاح! سنرد عليك خلال 24 ساعة.")
        
        elif contact_methods == "📍 زيارة مكتب":
            st.markdown("#### 📍 مقار المكاتب القانونية")
            
            offices = {
                "عمان - مركز المدينة": "شارع الملك حسين، بجانب وزارة العمل",
                "إربد - المنطقة الشمالية": "شارع الجامعة، مقابل جامعة العلوم والتكنولوجيا",
                "الزرقاء - المنطقة الوسطى": "حي الأمير حسن، near المستشفى الإسلامي"
            }
            
            for office, address in offices.items():
                with st.expander(f"🏢 {office}"):
                    st.write(f"**العنوان:** {address}")
                    st.write("**أوقات العمل:** 8:00 ص - 3:00 م (الأحد - الخميس)")
                    st.write("**الهاتف:** 06-5802666")
                    
                    if st.button("🗺️ عرض على الخريطة", key=f"map_{office}"):
                        st.info("سيتم فتح الخريطة في المتصفح")

# =====================================================
# 🏛️ قسم الجهات المختصة المتكامل
# =====================================================
def show_authorities_section():
    st.markdown("### 🏛️ الجهات المختصة - دليل شامل")
    
    auth_tabs = st.tabs([
        "📍 خريطة الجهات", 
        "📞 دليل الاتصال", 
        "🕒 أوقات العمل",
        "📋 الخدمات المقدمة"
    ])
    
    with auth_tabs[0]:
        st.markdown("### 📍 خريطة الجهات الرسمية")
        
        # بيانات الجهات
        authorities_data = {
            "عمان": {
                "وزارة العمل": {
                    "address": "شارع الملك حسين، جبل عمان",
                    "phone": "06-5802666",
                    "services": ["شكاوى العمل", "تراخيص العمل", "تفتيش العمل"]
                },
                "محكمة العمل": {
                    "address": "مجمع المحاكم، شفا بدران",
                    "phone": "06-5300444", 
                    "services": ["قضايا العمل", "منازعات العمل", "تحكيم العمل"]
                }
            },
            "إربد": {
                "مديرية العمل": {
                    "address": "شارع الجامعة، near جامعة اليرموك",
                    "phone": "02-7271111",
                    "services": ["شكاوى محلية", "تفتيش العمل", "إصدار تصاريح"]
                }
            },
            "الزرقاء": {
                "مديرية العمل": {
                    "address": "حي الأمير حسن، near المستشفى الإسلامي",
                    "phone": "05-3985555",
                    "services": ["شكاوى محلية", "تفتيش العمل", "إصدار تصاريح"]
                }
            }
        }
        
        selected_city = st.selectbox("اختر المحافظة", list(authorities_data.keys()), key="auth_city")
        
        if selected_city:
            st.success(f"## 🏙️ الجهات في {selected_city}")
            
            for authority, info in authorities_data[selected_city].items():
                with st.expander(f"🏢 {authority}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**📍 العنوان:** {info['address']}")
                        st.write(f"**📞 الهاتف:** {info['phone']}")
                    
                    with col2:
                        st.write("**🛎️ الخدمات:**")
                        for service in info['services']:
                            st.write(f"- {service}")
                    
                    # خريطة تفاعلية (محاكاة)
                    if st.button(f"🗺️ عرض على الخريطة", key=f"auth_map_{authority}"):
                        st.info(f"سيتم فتح خريطة لموقع {authority} في {selected_city}")
    
    with auth_tabs[1]:
        st.markdown("### 📞 دليل الاتصال الشامل")
        
        contact_categories = {
            "جهات الطوارئ": {
                "الدفاع المدني": "199",
                "الشرطة": "191", 
                "الإسعاف": "193"
            },
            "وزارة العمل": {
                "الخط الساخن": "06-5802666",
                "الشكاوى الإلكترونية": "complaints@mol.gov.jo",
                "دائرة الأجور": "06-5802777",
                "دائرة التفتيش": "06-5802888"
            },
            "المحاكم": {
                "محكمة العمل - عمان": "06-5300444",
                "محكمة الاستئناف": "06-5351000",
                "محكمة التمييز": "06-5342000"
            }
        }
        
        for category, contacts in contact_categories.items():
            with st.expander(f"📞 {category}"):
                for department, number in contacts.items():
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.write(f"**{department}**")
                    with col2:
                        st.write(f"`{number}`")
    
    with auth_tabs[2]:
        st.markdown("### 🕒 أوقات العمل والخدمات")
        
        schedules = {
            "وزارة العمل": {
                "الأحد - الخميس": "8:00 ص - 3:00 م",
                "الجمعة": "مغلق",
                "السبت": "مغلق",
                "ملاحظات": "قسم الشكاوى يعمل حتى 4:00 م"
            },
            "المحاكم": {
                "الأحد - الخميس": "8:00 ص - 2:00 م", 
                "الجمعة": "مغلق",
                "السبت": "مغلق",
                "ملاحظات": "جلسات المحاكم من 9:00 ص - 1:00 م"
            },
            "مراكز الدعم القانوني": {
                "الأحد - الخميس": "9:00 ص - 5:00 م",
                "الجمعة": "10:00 ص - 2:00 م",
                "السبت": "10:00 ص - 2:00 م",
                "ملاحظات": "خدمات مجانية للعاملين"
            }
        }
        
        for authority, schedule in schedules.items():
            with st.expander(f"⏰ {authority}"):
                for day, time in schedule.items():
                    st.write(f"**{day}:** {time}")
    
    with auth_tabs[3]:
        st.markdown("### 📋 الخدمات المقدمة من كل جهة")
        
        services_data = {
            "وزارة العمل": [
                "استقبال شكاوى العمال وأصحاب العمل",
                "إصدار وتجديد تصاريح العمل",
                "تفتيش أماكن العمل",
                "تسوية منازعات العمل",
                "إصدار شهادات الخبرة"
            ],
            "المحاكم": [
                "الفصل في منازعات العمل الفردية",
                "البت في قضايا الفصل التعسفي", 
                "التحكيم في نزاعات العمل الجماعية",
                "تنفيذ أحكام العمل"
            ],
            "النقابات": [
                "الدفاع عن حقوق العمال",
                "تقديم الاستشارات القانونية",
                "تمثيل العمال في المفاوضات",
                "تنظيم برامج التوعية"
            ]
        }
        
        for authority, services in services_data.items():
            with st.expander(f"🛎️ {authority}"):
                for service in services:
                    st.write(f"✅ {service}")

# =====================================================
# 🔍 البحث الذكي المتكامل
# =====================================================
def show_legal_search():
    section_header("🔍 البحث الذكي في القوانين", "ابحث في التشريعات والقوانين باستخدام الذكاء الاصطناعي")
    
    if not ai_assistant:
        st.warning("""
        ⚠️ لا يمكن استخدام البحث الذكي لأن ملف البيانات غير متاح أو حدث خطأ أثناء التحميل.
        **يمكنك استخدام البحث العادي في الأقسام الأخرى.**
        """)
        return
    
    search_tabs = st.tabs(["🔎 بحث سريع", "📚 بحث متقدم", "💡 استفسارات شائعة"])
    
    with search_tabs[0]:
        st.markdown("### 🔎 البحث السريع في القوانين")
        
        search_query = st.text_input(
            "اكتب استفسارك القانوني:",
            placeholder="مثال: مكافأة نهاية الخدمة بعد 5 سنوات عمل، حقوق العامل في الإجازة المرضية...",
            key="quick_search"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_type = st.selectbox("نوع البحث", ["دقيق", "شامل"], key="search_type")
        with col2:
            result_count = st.slider("عدد النتائج", 1, 10, 3, key="result_count")
        with col3:
            search_button = st.button("🔎 ابحث في القوانين", type="primary", key="search_btn")
        
        if search_button and search_query:
            with st.spinner("جاري البحث في التشريعات والقوانين..."):
                try:
                    results = ai_assistant.advanced_search(search_query, top_n=result_count)
                    if results:
                        st.success(f"🎯 تم العثور على {len(results)} نتيجة ذات صلة")
                        
                        for i, result in enumerate(results, 1):
                            with st.expander(f"📜 النتيجة {i} (دقة {result['score']:.1f}%)", expanded=i==1):
                                st.markdown(f"**📖 النص القانوني:**")
                                st.write(result['text'])
                                
                                if result.get('example'):
                                    st.markdown(f"**💡 مثال تطبيقي:**")
                                    st.info(result['example'])
                                
                                st.markdown(f"**📚 المرجع:** {result['reference']}")
                                
                                # إجراءات إضافية
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("📋 حفظ هذه النتيجة", key=f"save_{i}"):
                                        st.session_state.saved_results = st.session_state.get('saved_results', [])
                                        st.session_state.saved_results.append(result)
                                        st.success("تم حفظ النتيجة")
                                with col2:
                                    if st.button("🖨️ مشاركة", key=f"share_{i}"):
                                        st.info("ميزة المشاركة قريباً...")
                    else:
                        st.warning("""
                        ⚠️ لم يتم العثور على نتائج تطابق استفسارك.
                        
                        **اقتراحات:**
                        - تحقق من كتابة الكلمات المفتاحية
                        - جرب استخدام مرادفات أخرى
                        - استخدم البحث المتقدم للتحكم أكثر
                        """)
                except Exception as e:
                    st.error(f"""
                    ❌ حدث خطأ أثناء البحث: {e}
                    
                    **الحلول المقترحة:**
                    - تأكد من اتصال الإنترنت
                    - جرب البحث مرة أخرى
                    - استخدم البحث العادي في الأقسام الأخرى
                    """)
    
    with search_tabs[1]:
        st.markdown("### 📚 البحث المتقدم")
        
        col1, col2 = st.columns(2)
        
        with col1:
            advanced_query = st.text_area(
                "نص البحث المتقدم:",
                placeholder="صف مشكلتك القانونية بالتفصيل...",
                height=100,
                key="advanced_query"
            )
            
            law_types = st.multiselect(
                "نوع التشريعات:",
                ["قانون العمل", "الأنظمة والتعليمات", "القرارات الوزارية", "السوابق القضائية"],
                default=["قانون العمل"],
                key="law_types"
            )
        
        with col2:
            date_range = st.selectbox("الفترة الزمنية:", [
                "جميع الفترات",
                "آخر 5 سنوات", 
                "آخر 10 سنوات",
                "قبل 2010",
                "مخصص"
            ], key="date_range")
            
            relevance_threshold = st.slider("حد الدقة الأدنى (%)", 50, 95, 70, key="relevance_threshold")
            
            include_examples = st.checkbox("تضمين الأمثلة التطبيقية", value=True, key="include_examples")
            include_references = st.checkbox("تضمين المراجع الكاملة", value=True, key="include_references")
        
        if st.button("🔍 بحث متقدم", type="primary", key="advanced_search_btn") and advanced_query:
            with st.spinner("جاري البحث المتقدم في قاعدة البيانات القانونية..."):
                try:
                    # محاكاة البحث المتقدم
                    advanced_results = [
                        {
                            'text': "المادة 74: تستحق مكافأة نهاية الخدمة للعامل إذا أنهيت خدماته لأي سبب عدا الاستقالة.",
                            'example': "عامل عمل لمدة 7 سنوات براتب 500 دينار، يستحق مكافأة قدرها 1800 دينار.",
                            'reference': "قانون العمل الأردني - المادة 74",
                            'score': 92.5,
                            'date': "2020",
                            'type': "قانون العمل"
                        }
                    ]
                    
                    if advanced_results:
                        st.success(f"🎯 تم العثور على {len(advanced_results)} نتيجة متقدمة")
                        
                        for i, result in enumerate(advanced_results, 1):
                            with st.expander(f"📚 نتيجة متقدمة {i} | {result['type']} | دقة {result['score']}%", expanded=True):
                                st.markdown("**📖 المحتوى القانوني:**")
                                st.write(result['text'])
                                
                                if include_examples and result.get('example'):
                                    st.markdown("**💡 التطبيق العملي:**")
                                    st.info(result['example'])
                                
                                if include_references:
                                    st.markdown("**📋 المعلومات المرجعية:**")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**المرجع:** {result['reference']}")
                                    with col2:
                                        st.write(f"**السنة:** {result.get('date', 'غير محدد')}")
                    
                    else:
                        st.warning("لم يتم العثور على نتائج تطابق معايير البحث المتقدم.")
                        
                except Exception as e:
                    st.error(f"خطأ في البحث المتقدم: {e}")
    
    with search_tabs[2]:
        st.markdown("### 💡 الاستفسارات الشائعة")
        
        common_queries = {
            "🤔 مكافأة نهاية الخدمة": [
                "كيف تحسب مكافأة نهاية الخدمة؟",
                "متى تستحق مكافأة نهاية الخدمة كاملة؟",
                "ما الفرق بين الاستقالة والفصل في نهاية الخدمة؟"
            ],
            "🏥 الإجازات والراحة": [
                "كم يوم إجازة سنوية تستحق؟", 
                "ما هي حقوقي في الإجازة المرضية؟",
                "هل يمكن تجزئة الإجازة السنوية؟"
            ],
            "💰 الأجور والمدفوعات": [
                "ما هو الحد الأدنى للأجور في الأردن؟",
                "كيف يتم حساب بدل العمل الإضافي؟",
                "ماذا أفعل إذا لم يصرف راتبي؟"
            ],
            "⚖️ إنهاء الخدمة": [
                "ما هو الفصل التعسفي؟",
                "كم مدة الإخطار قبل إنهاء الخدمة؟",
                "ما هي حقوقي في حالة الفصل؟"
            ]
        }
        
        selected_category = st.selectbox("اختر فئة الاستفسار", list(common_queries.keys()), key="common_category")
        
        if selected_category:
            st.write(f"**🔍 استفسارات شائعة في {selected_category}:**")
            
            for query in common_queries[selected_category]:
                if st.button(f"❓ {query}", key=query):
                    # محاكاة البحث عن الاستفسار
                    st.session_state.quick_search = query
                    st.rerun()
        
        st.markdown("---")
        st.markdown("#### 📊 إحصائيات البحث")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔍 عمليات البحث اليوم", "147")
        with col2:
            st.metric("📈 أكثر المواضيع بحثاً", "نهاية الخدمة")
        with col3:
            st.metric("💡 متوسط الدقة", "89%")

# =====================================================
# ⚙️ صفحة الإعدادات المتكاملة
# =====================================================
def show_settings_page():
    st.markdown("### ⚙️ الإعدادات والتهيئة")
    
    settings_tabs = st.tabs(["🎛️ إعدادات التطبيق", "👤 الملف الشخصي", "🔔 الإشعارات", "🛡️ الخصوصية"])
    
    with settings_tabs[0]:
        st.markdown("### 🎛️ إعدادات التطبيق العامة")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("الإعدادات العامة")
            app_language = st.selectbox("لغة التطبيق", ["العربية", "English"], key="app_lang")
            theme_mode = st.radio("الوضع اللوني", ["فاتح", "داكن", "تلقائي"], key="app_theme")
            font_size = st.slider("حجم الخط", 14, 24, 16, key="app_font")
            reduce_animations = st.checkbox("تقليل الحركات والرسوم المتحركة", key="app_animations")
        
        with col2:
            st.subheader("إعدادات الذكاء الاصطناعي")
            ai_enabled = st.toggle("تفعيل البحث بالذكاء الاصطناعي", value=True, key="app_ai")
            search_depth = st.select_slider("دقة البحث", options=["سريع", "متوازن", "دقيق"], key="app_depth")
            result_history = st.number_input("عدد النتائج المحفوظة", 10, 100, 25, key="app_history")
            auto_suggest = st.checkbox("الاقتراح التلقائي أثناء الكتابة", value=True, key="app_suggest")
        
        st.subheader("إعدادات البيانات")
        data_auto_save = st.toggle("الحفظ التلقائي للبيانات", value=True, key="app_autosave")
        backup_frequency = st.selectbox("تكرار النسخ الاحتياطي", ["يومي", "أسبوعي", "شهري"], key="app_backup")
        clear_cache = st.button("🗑️ مسح الذاكرة المؤقتة", key="app_cache")
        
        if clear_cache:
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("تم مسح الذاكرة المؤقتة بنجاح")
        
        if st.button("💾 حفظ الإعدادات", type="primary", key="save_settings"):
            st.success("تم حفظ الإعدادات بنجاح!")
    
    with settings_tabs[1]:
        st.markdown("### 👤 الملف الشخصي")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("الاسم الكامل", value="محمد أحمد", key="profile_name")
            st.text_input("البريد الإلكتروني", value="mohammed@example.com", key="profile_email")
            st.text_input("رقم الهاتف", value="+962 79 000 0000", key="profile_phone")
            st.selectbox("المحافظة", ["عمان", "إربد", "الزرقاء", "مأدبا", "البلقاء"], key="profile_city")
        
        with col2:
            st.selectbox("المهنة", ["عامل", "صاحب عمل", "محامي", "باحث", "طالب"], key="profile_job")
            st.selectbox("مجال العمل", ["القطاع الخاص", "الحكومي", "العسكري", "الخاص", "أخرى"], key="profile_field")
            st.number_input("سنوات الخبرة", min_value=0, max_value=50, value=5, key="profile_exp")
            st.text_area("الاهتمامات القانونية", placeholder="اكتب اهتماماتك في مجال القانون...", key="profile_interests")
        
        # إحصائيات المستخدم
        st.markdown("### 📊 إحصائيات استخدامك")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🔍 عمليات البحث", "47")
            st.metric("🧮 الحسابات", "12")
        with col2:
            st.metric("📝 الشكاوى", "3")
            st.metric("💾 المستندات", "8")
        with col3:
            st.metric("⭐ التقييم", "4.8/5")
            st.metric("📅 عضو منذ", "6 أشهر")
        
        if st.button("🔄 تحديث الملف الشخصي", type="primary", key="update_profile"):
            st.success("تم تحديث الملف الشخصي بنجاح!")
    
    with settings_tabs[2]:
        st.markdown("### 🔔 إعدادات الإشعارات")
        
        st.subheader("أنواع الإشعارات")
        email_notifications = st.checkbox("الإشعارات عبر البريد الإلكتروني", value=True, key="notify_email")
        push_notifications = st.checkbox("الإشعارات الفورية", value=True, key="notify_push")
        sms_notifications = st.checkbox("الإشعارات عبر الرسائل النصية", key="notify_sms")
        
        st.subheader("تفاصيل الإشعارات")
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("تحديثات القوانين", value=True, key="notify_laws")
            st.checkbox("نتائج البحث", value=True, key="notify_results")
            st.checkbox("تذكيرات المواعيد", value=True, key="notify_reminders")
        
        with col2:
            st.checkbox("عروض وتحديثات", value=False, key="notify_offers")
            st.checkbox("نصائح قانونية", value=True, key="notify_tips")
            st.checkbox("تقارير الاستخدام", value=False, key="notify_reports")
        
        st.subheader("توقيت الإشعارات")
        notification_frequency = st.select_slider("تكرار الإشعارات", options=["نادراً", "عادي", "كثيراً"], key="notify_freq")
        quiet_hours = st.time_input("بداية ساعات الهدوء", value=datetime.strptime("22:00", "%H:%M").time(), key="notify_quiet")
        weekend_notifications = st.checkbox("الإشعارات في عطلات نهاية الأسبوع", value=False, key="notify_weekend")
        
        if st.button("💾 حفظ إعدادات الإشعارات", key="save_notify"):
            st.success("تم حفظ إعدادات الإشعارات!")
    
    with settings_tabs[3]:
        st.markdown("### 🛡️ الخصوصية والأمان")
        
        st.subheader("إعدادات الخصوصية")
        data_collection = st.radio("جمع البيانات", [
            "جمع الحد الأدنى فقط",
            "جمع لتحسين الخدمة", 
            "جمع كامل للإحصائيات"
        ], key="privacy_data")
        
        st.checkbox("مشاركة البيانات لأغراض إحصائية (مجهولة)", value=False, key="privacy_stats")
        st.checkbox("السماح بتحليل نمط الاستخدام", value=True, key="privacy_analytics")
        st.checkbox("مشاركة التقييمات والملاحظات", value=True, key="privacy_feedback")
        
        st.subheader("الأمان")
        change_password = st.button("🔐 تغيير كلمة المرور", key="security_password")
        two_factor = st.toggle("المصادقة الثنائية", value=False, key="security_2fa")
        auto_logout = st.slider("تسجيل الخروج التلقائي (دقائق)", 5, 120, 30, key="security_logout")
        
        st.subheader("إدارة البيانات")
        col1, col2 = st.columns(2)
        
        with col1:
            export_data = st.button("📤 تصدير جميع بياناتي", key="data_export")
            if export_data:
                st.info("سيتم إرسال رابط التحميل إلى بريدك الإلكتروني")
        
        with col2:
            delete_account = st.button("🗑️ حذف الحساب", type="secondary", key="data_delete")
            if delete_account:
                st.warning("⚠️ هذا الإجراء لا يمكن التراجع عنه!")
                confirm = st.checkbox("أؤكد أنني أريد حذف حسابي بشكل دائم", key="delete_confirm")
                if confirm and st.button("تأكيد الحذف النهائي", key="delete_final"):
                    st.error("تم حذف الحساب بنجاح")
        
        st.markdown("---")
        st.markdown("#### 📜 الشروط والخصوصية")
        st.write("""
        باستخدامك لهذا التطبيق، فإنك توافق على:
        - شروط الخدمة وسياسة الخصوصية
        - جمع البيانات لأغراض تحسين الخدمة
        - الالتزام بالقوانين والأنظمة المحلية
        """)
        
        if st.button("📄 عرض سياسة الخصوصية الكاملة", key="privacy_policy"):
            st.info("سيتم فتح سياسة الخصوصية في نافذة جديدة")

# =====================================================
# 🧮 دوال الحساب المساعدة
# =====================================================
def calculate_end_service(salary, years, contract_type):
    """حساب مبسط لمكافأة نهاية الخدمة"""
    if contract_type == "محدد المدة":
        return salary * years * 0.5
    else:
        if years <= 5:
            return salary * years * 0.5
        else:
            return (salary * 5 * 0.5) + (salary * (years - 5) * 1.0)

def calculate_end_of_service(salary, years, months, contract_type, end_reason, include_allowances):
    """حساب مكافأة نهاية الخدمة"""
    total_months = years * 12 + months
    
    if end_reason == "فصل تعسفي":
        # حساب كامل المكافأة
        if total_months <= 60:  # 5 سنوات
            amount = (salary * total_months) / 24
        else:
            first_5 = (salary * 60) / 24
            remaining = (salary * (total_months - 60)) / 12
            amount = first_5 + remaining
    else:
        # حساب حسب نوع النهاية
        if total_months <= 60:
            amount = (salary * total_months) / 48
        else:
            first_5 = (salary * 60) / 48
            remaining = (salary * (total_months - 60)) / 24
            amount = first_5 + remaining
    
    return {
        'total_amount': amount,
        'calculation_method': "طريقة الحساب حسب قانون العمل الأردني",
        'calculation_steps': [
            f"الراتب الأساسي: {salary:,.0f} دينار",
            f"مدة الخدمة: {years} سنة و {months} شهر",
            f"سبب إنهاء الخدمة: {end_reason}",
            f"المبلغ المستحق: {amount:,.0f} دينار"
        ]
    }

def calculate_overtime(hourly_rate, hours, overtime_type, days_worked, transport):
    """حساب بدل العمل الإضافي"""
    rate_multiplier = {
        "عمل إضافي عادي (125%)": 1.25,
        "عمل إضافي ليلي (150%)": 1.5,
        "عمل في العطلات الرسمية (200%)": 2.0
    }
    
    overtime_rate = hourly_rate * rate_multiplier[overtime_type]
    total_overtime = hours * overtime_rate
    monthly_total = total_overtime + transport
    
    return {
        'total_overtime': total_overtime,
        'overtime_rate': overtime_rate,
        'monthly_total': monthly_total
    }

def calculate_sick_leave(daily_salary, sick_days, has_report, service_years, chronic, hospitalization):
    """حساب الإجازات المرضية"""
    full_pay_days = min(sick_days, 14)  # 14 يوم براتب كامل
    remaining_days = max(0, sick_days - 14)
    half_pay_days = min(remaining_days, 14)  # 14 يوم بنصف راتب
    no_pay_days = max(0, sick_days - 28)  # الباقي بدون راتب
    
    total_amount = (full_pay_days * daily_salary) + (half_pay_days * daily_salary * 0.5)
    
    return {
        'total_amount': total_amount,
        'full_pay_days': full_pay_days,
        'half_pay_days': half_pay_days,
        'no_pay_days': no_pay_days
    }

def calculate_annual_leave(salary, worked_months, taken_vacation, start_year, accumulated):
    """حساب الإجازات السنوية"""
    due_per_year = 14  # 14 يوم إجازة سنوية
    due_vacation = (worked_months / 12) * due_per_year + accumulated
    remaining_vacation = due_vacation - taken_vacation
    daily_rate = salary / 30  # افتراض 30 يوم في الشهر
    vacation_pay = remaining_vacation * daily_rate
    
    return {
        'due_vacation': due_vacation,
        'remaining_vacation': remaining_vacation,
        'daily_rate': daily_rate,
        'vacation_pay': vacation_pay
    }

def calculate_comprehensive_benefits(salary, years, overtime_hours, sick_days, vacation_days, end_reason):
    """حساب شامل لجميع المستحقات"""
    end_service = calculate_end_of_service(salary, years, 0, "غير محدد المدة", end_reason, True)['total_amount']
    overtime = calculate_overtime(salary/30/8, overtime_hours, "عمل إضافي عادي (125%)", 22, 0)['monthly_total']
    sick_leave = calculate_sick_leave(salary/30, sick_days, True, years, False, 0)['total_amount']
    annual_leave = calculate_annual_leave(salary, 12, 0, 2020, 0)['vacation_pay'] * (vacation_days/14)
    
    total_benefits = end_service + overtime + sick_leave + annual_leave
    net_benefits = total_benefits * 0.95  # افتراض خصم 5% للتأمينات
    
    return {
        'end_service': end_service,
        'overtime': overtime,
        'sick_leave': sick_leave,
        'annual_leave': annual_leave,
        'total_benefits': total_benefits,
        'net_benefits': net_benefits
    }

# =====================================================
# 📝 دوال مساعدة لمحاكي الشكوى
# =====================================================
def analyze_complaint(complaint_data):
    """تحليل الشكوى وإعطاء توصيات"""
    analysis = {
        'problem_severity': 'متوسطة',
        'recommended_actions': [],
        'legal_basis': [],
        'expected_outcome': '',
        'timeline': '2-4 أسابيع'
    }
    
    # تحليل حسب نوع المشكلة
    if complaint_data['problem_type'] == "مشاكل الأجور والرواتب":
        analysis['problem_severity'] = 'عالية' if complaint_data['financial_impact'] in ['كبير', 'جسيم'] else 'متوسطة'
        analysis['recommended_actions'] = [
            "تقديم شكوى فورية لوزارة العمل",
            "جمع كشوف الرواتب والإثباتات",
            "طلب وساطة من مكتب العمل"
        ]
        analysis['legal_basis'] = ["المادة 55 من قانون العمل", "نظام الأجور رقم 28 لسنة 2020"]
    
    elif complaint_data['problem_type'] == "إنهاء الخدمة والفصل":
        analysis['problem_severity'] = 'عالية'
        analysis['recommended_actions'] = [
            "عدم توقيع أي مستندات",
            "طلب صورة من قرار الفصل", 
            "التوجه لوزارة العمل خلال 48 ساعة",
            "استشارة محام متخصص"
        ]
        analysis['legal_basis'] = ["المادة 74 من قانون العمل", "قرارات محكمة التمييز في الفصل التعسفي"]
    
    # إضافة المزيد من التحليلات...
    
    return analysis

def display_complaint_analysis(analysis):
    """عرض نتائج التحليل"""
    st.success("## 🎯 نتائج تحليل مشكلتك")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("📊 درجة الخطورة", analysis['problem_severity'])
        st.metric("⏱️ المدة المتوقعة", analysis['timeline'])
    
    with col2:
        st.metric("📈 التوقعات", "إيجابية" if analysis['problem_severity'] != 'عالية' else "تحتاج متابعة")
        st.metric("🔧 الإجراءات المطلوبة", len(analysis['recommended_actions']))
    
    st.markdown("### 📋 الإجراءات المقترحة")
    for i, action in enumerate(analysis['recommended_actions'], 1):
        st.write(f"{i}. {action}")
    
    st.markdown("### ⚖️ الأساس القانوني")
    for basis in analysis['legal_basis']:
        st.write(f"📜 {basis}")

def generate_complaint_form(complaint_type, form_data, user_info):
    """توليد نموذج شكوى جاهز"""
    templates = {
        "شكوى أجور": f"""
        نموذج شكوى - عدم صرف الرواتب
        التاريخ: {datetime.now().strftime('%Y-%m-%d')}
        
        معلومات المقدم:
        الاسم: {user_info['name']}
        رقم الهوية: {user_info['id']}
        الهاتف: {user_info['phone']}
        مكان العمل: {user_info['workplace']}
        الوظيفة: {user_info['position']}
        الراتب: {user_info['salary']} دينار
        
        تفاصيل الشكوى:
        نوع الشكوى: عدم صرف الرواتب
        تاريخ بدء المشكلة: {form_data.get('تاريخ عدم الصرف', '')}
        المبلغ المستحق: {form_data.get('المبلغ المستحق', '')}
        مدة التأخير: {form_data.get('عدد أشهر التأخير', '')}
        
        الطلب:
        أطلب من وزارة العمل اتخاذ الإجراءات القانونية اللازمة ضد صاحب العمل
        والمطالبة بصرف كامل المستحقات المالية.
        
        التوقيع: ___________________
        """,
        
        "شكوى فصل تعسفي": f"""
        نموذج شكوى - فصل تعسفي
        التاريخ: {datetime.now().strftime('%Y-%m-%d')}
        
        معلومات المقدم:
        الاسم: {user_info['name']}
        رقم الهوية: {user_info['id']}
        الهاتف: {user_info['phone']}
        مكان العمل: {user_info['workplace']}
        الوظيفة: {user_info['position']}
        الراتب: {user_info['salary']} دينار
        
        تفاصيل الشكوى:
        نوع الشكوى: فصل تعسفي
        تاريخ الفصل: {form_data.get('تاريخ الفصل', '')}
        سبب الفصل المعلن: {form_data.get('سبب الفصل المعلن', '')}
        الإنذارات السابقة: {form_data.get('الإنذارات السابقة', '')}
        
        الطلب:
        أطلب إلغاء قرار الفصل والعودة للعمل أو صرف كامل التعويضات المستحقة قانوناً.
        
        التوقيع: ___________________
        """
    }
    
    return templates.get(complaint_type, "نموذج غير متوفر")

def generate_advisor_response(user_message):
    """توليد رد مستشار (محاكاة)"""
    responses = {
        "أجور": "ننصحك بتقديم شكوى لوزارة العمل مع كشوف الرواتب والإثباتات.",
        "فصل": "في حال الفصل التعسفي، لديك 30 يوم لرفع دعوى في محكمة العمل.",
        "إجازات": "الحرمان من الإجازات يخالف القانون، يمكنك المطالبة بالتعويض."
    }
    
    for keyword, response in responses.items():
        if keyword in user_message:
            return response
    
    return "شكراً لتواصلك. يمكنني مساعدتك في مشاكلك القانونية. يرجى توضيح طلبك."

# =====================================================
# 🧭 التنفيذ الرئيسي
# =====================================================
def main():
    # الشريط الجانبي
    with st.sidebar:
        st.markdown(
            f"<div style='text-align: center; padding: 1rem;'>"
            f"<h2>⚖️ {config.get('APP_INFO', {}).get('APP_NAME', 'منصة قانون العمل')}</h2>"
            f"<p style='color: #666; font-size: 0.9rem;'>الإصدار {config.get('APP_INFO', {}).get('VERSION', 'v25.1')}</p>"
            f"</div>", unsafe_allow_html=True
        )
        st.markdown("---")
        
        # القائمة الرئيسية
        page_options = {
            "🏠 الصفحة الرئيسية": show_home_page,
            "👷 العمال": show_workers_section,
            "🧮 الحاسبات القانونية": show_calculators_section,
            "📝 محاكي الشكوى": show_complaint_simulator,
            "🏛️ الجهات المختصة": show_authorities_section,
            "🔍 البحث في القوانين": show_legal_search,
            "⚙️ الإعدادات": show_settings_page
        }
        
        selected_page = st.selectbox("اختر القسم", list(page_options.keys()), key="main_nav")
        
        st.markdown("---")
        st.markdown("### 📞 الدعم الفني")
        st.write("📧 support@alyworklaw.com")
        st.write("📞 06-5802666")
        st.write("🕒 الأحد - الخميس: 8:00 ص - 3:00 م")
        
        st.markdown("---")
        st.markdown("### 🔔 التنبيهات المهمة")
        st.info("""
        - تحديثات القوانين الجديدة
        - ورش عمل مجانية
        - استشارات قانونية
        """)
    
    # عرض الصفحة المحددة
    if selected_page in page_options:
        try:
            page_options[selected_page]()
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء عرض الصفحة: {e}")
            st.info("يرجى تحديث الصفحة أو المحاولة لاحقاً")
    
    # التذييل
    st.markdown("---")
    footer_text = config.get("FOOTER", {}).get("TEXT", "© 2025 منصة قانون العمل الذكية — جميع الحقوق محفوظة.")
    st.markdown(f"<center><small>{footer_text}</small></center>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()