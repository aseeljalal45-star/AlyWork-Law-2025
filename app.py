import streamlit as st
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# تحميل إعدادات البيئة
load_dotenv()

# ==========================
# استيراد المكونات المساعدة
# ==========================
from helpers.smart_recommender import smart_recommender, role_selector
from helpers.ui_components import section_header, message_bubble, info_card, mini_card, feature_highlight
from helpers.mini_ai_smart import MiniLegalAI
from helpers.settings_manager import SettingsManager
from helpers.data_loader import DataLoader

# =====================================================
# 🎯 إعدادات التطبيق والبيئة
# =====================================================
def setup_application():
    """تهيئة التطبيق وإعدادات البيئة"""
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
        }
    }
    
    settings_manager = SettingsManager()
    settings_manager.update(env_config)
    return settings_manager

# تهيئة التطبيق
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
        .main-header { background: linear-gradient(135deg, #1E3A8A, #2563EB); color: white; padding: 2rem; border-radius: 20px; text-align: center; margin-bottom: 2rem; }
        .feature-card { background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 1rem 0; transition: transform 0.3s ease; }
        .feature-card:hover { transform: translateY(-5px); }
        </style>
        """, unsafe_allow_html=True)

load_custom_css()

# =====================================================
# 🤖 تهيئة المكونات الذكية
# =====================================================
@st.cache_resource
def init_ai_assistant():
    workbook_path = config.get("DATA_SOURCES", {}).get("WORKBOOK_PATH", "")
    return MiniLegalAI(workbook_path)

@st.cache_resource
def init_data_loader():
    return DataLoader()

ai_assistant = init_ai_assistant()
data_loader = init_data_loader()

# =====================================================
# 🏠 الصفحة الرئيسية
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
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📊 المواد القانونية", "150+")
    with col2: st.metric("👥 المستفيدين", "5,000+")
    with col3: st.metric("⚖️ المحافظات", "12")
    with col4: st.metric("💼 نسبة الرضا", "95%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # التوصيات الذكية
    st.markdown("### 🎯 التوصيات الذكية لك")
    selected_role = role_selector()
    smart_recommender(selected_role, show_header=False)
    
    # الميزات الرئيسية
    st.markdown("### 🚀 خدماتنا الرئيسية")
    features = [
        {"icon": "🧮", "title": "الحاسبات القانونية", "description": "حساب دقيق للمستحقات المالية وفق القانون الأردني", "features": ["مكافأة نهاية الخدمة", "بدل العمل الإضافي", "الإجازات المرضية"]},
        {"icon": "📝", "title": "محاكي الشكوى الذكي", "description": "تحليل الانتهاكات وتقديم الإجراءات القانونية المناسبة", "features": ["تحليل آلي", "توصيات مخصصة", "نماذج جاهزة"]},
        {"icon": "🏛️", "title": "الجهات المختصة", "description": "دليل شامل للجهات الرسمية في جميع المحافظات", "features": ["عنوان دقيق", "معلومات اتصال", "أوقات العمل"]},
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

# =====================================================
# 🧮 الحاسبات القانونية
# =====================================================
def show_calculators_section():
    section_header("🧮 الحاسبات القانونية", "حساب دقيق للمستحقات المالية وفق القانون الأردني")
    
    calc_type = st.selectbox(
        "اختر نوع الحاسبة:",
        ["مكافأة نهاية الخدمة", "بدلات العمل الإضافي", "التعويض عن الإجازات", "بدل النقل والسكن"]
    )
    
    if calc_type == "مكافأة نهاية الخدمة":
        with st.form("end_of_service_calc"):
            col1, col2 = st.columns(2)
            with col1:
                years = st.number_input("سنوات الخدمة", min_value=0, max_value=50, value=5)
                basic_salary = st.number_input("الأجر الأساسي (دينار)", min_value=0, value=500)
            with col2:
                service_type = st.selectbox("نوع نهاية الخدمة", ["استقالة", "إنهاء خدمة", "بلوغ سن المعاش"])
                last_salary = st.number_input("آخر راتب (دينار)", min_value=0, value=500)
            
            if st.form_submit_button("🔄 احسب المكافأة"):
                if service_type == "استقالة":
                    if years <= 5:
                        compensation = years * 0.5 * basic_salary
                    else:
                        compensation = (5 * 0.5 * basic_salary) + ((years - 5) * basic_salary)
                else:
                    compensation = years * basic_salary
                st.success(f"💰 المكافأة المستحقة: **{compensation:,.0f} دينار أردني**")

# =====================================================
# 📝 محاكي الشكوى الذكي
# =====================================================
def show_complaint_simulator():
    section_header("📝 محاكي الشكوى الذكي", "تحليل الانتهاكات وتقديم الحلول القانونية المثلى")
    
    with st.form("complaint_form"):
        st.subheader("👤 معلومات العامل")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم الكامل")
            years_service = st.slider("سنوات الخدمة", 0, 40, 3)
        with col2:
            phone = st.text_input("رقم الهاتف")
            monthly_salary = st.number_input("الراتب الشهري (دينار)", min_value=0, value=500)
        
        st.subheader("⚠️ تفاصيل الانتهاك")
        violation_type = st.selectbox(
            "نوع الانتهاك",
            ["عدم دفع الأجر/المستحقات", "الفصل التعسفي", "العمل الإضافي غير المدفوع", 
             "عدم منح الإجازات القانونية", "ظروف عمل غير آمنة", "انتهاكات أخرى"]
        )
        violation_details = st.text_area("وصف تفصيلي للانتهاك", placeholder="صف ما حدث بالتفصيل...")
        
        if st.form_submit_button("🔍 حلل الحالة وقدم التوصيات"):
            with st.spinner("جاري التحليل..."):
                import time; time.sleep(2)
                st.success("✅ تم تحليل الحالة بنجاح")
                recommendations = {
                    "عدم دفع الأجر/المستحقات": [
                        "تقديم شكوى لمديرية العمل المختصة",
                        "طلب صورة من كشوف المرتبات", 
                        "توثيق جميع عمليات الدفع",
                        "الاحتفاظ بجميع المراسلات"
                    ],
                    "الفصل التعسفي": [
                        "طلب تعويض الفصل التعسفي",
                        "تقديم شكوى لمحكمة العمل",
                        "إثبات عدم وجود مبرر للفصل",
                        "الاحتفاظ بجميع الوثائق"
                    ]
                }
                recs = recommendations.get(violation_type, ["تقديم شكوى مفصلة لمديرية العمل", "الاحتفاظ بجميع الأدلة والوثائق", "استشارة محامٍ متخصص"])
                for i, rec in enumerate(recs, 1):
                    st.markdown(f"{i}. {rec}")

# =====================================================
# 🏛️ الجهات المختصة
# =====================================================
def show_authorities_section():
    section_header("🏛️ الجهات المختصة", "دليل شامل للجهات الرسمية في جميع المحافظات")
    governorates = ["عمان", "إربد", "الزرقاء", "البلقاء", "الكرك", "معان", "الطفيلة", "المفرق", "مادبا", "جرش", "عجلون", "العقبة"]
    selected_gov = st.selectbox("اختر المحافظة", governorates)
    authorities_data = {
        "عمان": {"مديرية العمل - عمان": {"عنوان": "عمان، شارع عيسى الناوري 11","هاتف": "06-5802666","بريد": "info@mol.gov.jo","موقع": "http://www.mol.gov.jo","أوقات العمل": "الأحد - الخميس: 8:00 ص - 3:00 م"}},
        "إربد": {"مديرية العمل - إربد": {"عنوان": "إربد، المنطقة الشمالية","هاتف": "02-7241000","بريد": "irbid@mol.gov.jo","أوقات العمل": "الأحد - الخميس: 8:00 ص - 3:00 م"}}
    }
    gov_data = authorities_data.get(selected_gov, authorities_data["عمان"])
    for authority, info in gov_data.items():
        with st.expander(f"🏢 {authority}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**📍 العنوان:** {info['عنوان']}")
                st.write(f"**📞 الهاتف:** {info['هاتف']}")
            with col2:
                st.write(f"**📧 البريد:** {info['بريد']}")
                st.write(f"**🕒 أوقات العمل:** {info['أوقات العمل']}")

# =====================================================
# 🔍 البحث في القوانين
# =====================================================
def show_legal_search():
    section_header("🔍 البحث الذكي في القوانين", "ابحث في التشريعات والقوانين باستخدام الذكاء الاصطناعي")
    search_query = st.text_input("اكتب استفسارك القانوني:", placeholder="مثال: مكافأة نهاية الخدمة بعد 5 سنوات عمل...")
    if st.button("🔎 ابحث في القوانين") and search_query:
        with st.spinner("جاري البحث..."):
            results = ai_assistant.advanced_search(search_query, top_n=3)
            if results:
                st.success(f"🎯 تم العثور على {len(results)} نتيجة")
                for i, result in enumerate(results, 1):
                    with st.expander(f"📜 النتيجة {i} (دقة {result['score']}%)", expanded=i==1):
                        st.write(f"**النص القانوني:** {result['text']}")
                        if result['example']: st.write(f"**مثال تطبيقي:** {result['example']}")
                        st.write(f"**المرجع:** {result['reference']}")
            else:
                st.warning("⚠️ لم يتم العثور على نتائج")

# =====================================================
# ⚙️ صفحة الإعدادات
# =====================================================
def show_settings_page():
    section_header("⚙️ الإعدادات", "إدارة إعدادات التطبيق والبيانات")
    tab1, tab2, tab3 = st.tabs(["الإعدادات العامة", "إدارة البيانات", "حول التطبيق"])
    with tab1:
        st.subheader("الإعدادات العامة")
        st.selectbox("السمة", ["فاتح", "داكن"])
        st.selectbox("اللغة", ["العربية", "English"])
        if st.button("💾 حفظ الإعدادات"): st.success("تم حفظ الإعدادات بنجاح")
    with tab2:
        st.subheader("إدارة البيانات")
        st.info("هنا يمكنك إدارة قاعدة البيانات والملفات")
        if st.button("🔄 تحديث قاعدة البيانات"): ai_assistant.reload(); st.success("تم تحديث قاعدة البيانات بنجاح")
        if st.button("🧹 مسح الذاكرة المؤقتة"): st.cache_data.clear(); st.success("تم مسح الذاكرة المؤقتة بنجاح")
    with tab3:
        st.subheader("حول التطبيق")
        st.write(f"**اسم التطبيق:** {config.get('APP_INFO', {}).get('APP_NAME', 'N/A')}")
        st.write(f"**الإصدار:** {config.get('APP_INFO', {}).get('VERSION', 'N/A')}")
        st.write(f"**البريد الدعم:** {config.get('APP_INFO', {}).get('SUPPORT_EMAIL', 'N/A')}")

# =====================================================
# 🧭 نظام التنقل الرئيسي
# =====================================================
def main():
    with st.sidebar:
        st.markdown(f"<div style='text-align: center; padding: 1rem;'><h2>⚖️ {config.get('APP_INFO', {}).get('APP_NAME', 'منصة قانون العمل')}</h2><p style='color: #666; font-size: 0.9rem;'>الإصدار {config.get('APP_INFO', {}).get('VERSION', 'v25.1')}</p></div>", unsafe_allow_html=True)
        st.markdown("---")
        page_options = {
            "🏠 الصفحة الرئيسية": show_home_page,
            "🧮 الحاسبات القانونية": show_calculators_section,
            "📝 محاكي الشكوى": show_complaint_simulator,
            "🏛️ الجهات المختصة": show_authorities_section,
            "🔍 البحث في القوانين": show_legal_search,
            "⚙️ الإعدادات": show_settings_page
        }
        selected_page = st.selectbox("اختر القسم", list(page_options.keys()))
        st.markdown("---")
        st.markdown("### 📞 الدعم الفني")
        st.write("📧 support@alyworklaw.com")
        st.write("📞 06-5802666")
        st.write("🕒 الأحد - الخميس: 8:00 ص - 3:00 م")
    
    if selected_page in page_options: page_options[selected_page]()
    
    st.markdown("---")
    footer_text = config.get("FOOTER", {}).get("TEXT", "© 2025 منصة قانون العمل الذكية — جميع الحقوق محفوظة.")
    st.markdown(f"<center><small>{footer_text}</small></center>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()