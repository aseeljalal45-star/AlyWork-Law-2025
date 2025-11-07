import streamlit as st
import os
import pandas as pd
from helpers.mini_ai_smart import MiniLegalAI
from helpers.settings_manager import SettingsManager
from helpers.ui_components import section_header, message_bubble, info_card
import plotly.express as px

# =====================================================
# ⚙️ الإعدادات العامة
# =====================================================
settings = SettingsManager()
config = st.session_state.get("config", settings.settings)

st.set_page_config(
    page_title=config.get("APP_NAME", "منصة قانون العمل الأردني الذكية"),
    page_icon="⚖️",
    layout="wide"
)

# =====================================================
# 🎨 تحميل CSS الرسمي
# =====================================================
def load_official_css(css_file="assets/styles_official.css"):
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_official_css()

# =====================================================
# 📊 تحميل البيانات
# =====================================================
def sheet_to_csv_url(sheet_url):
    import re
    if "docs.google.com/spreadsheets" in sheet_url and "export?format=csv" not in sheet_url:
        m = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
        if m:
            return f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=csv"
    return sheet_url

SHEET_URL = settings.get("SHEET_URL", config.get("SHEET_URL"))
WORKBOOK_PATH = settings.get("WORKBOOK_PATH", config.get("WORKBOOK_PATH"))

@st.cache_data(ttl=config.get("CACHE", {}).get("TTL_SECONDS", 600))
def load_google_sheets(url):
    if not url:
        st.info("ℹ️ لم يتم تحديد رابط Google Sheet بعد.")
        return pd.DataFrame()
    try:
        url = sheet_to_csv_url(url)
        return pd.read_csv(url)
    except Exception as e:
        st.warning(f"⚠️ خطأ أثناء تحميل Google Sheet: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=config.get("CACHE", {}).get("TTL_SECONDS", 600))
def load_excel(path, expected_cols=None):
    expected_cols = expected_cols or ['المادة', 'القسم', 'النص', 'مثال']
    if not os.path.exists(path):
        return pd.DataFrame(columns=expected_cols)
    try:
        df = pd.read_excel(path, engine='openpyxl')
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        df.fillna("", inplace=True)
        return df
    except Exception as e:
        st.warning(f"⚠️ خطأ أثناء قراءة Excel: {e}")
        return pd.DataFrame(columns=expected_cols)

data = load_google_sheets(SHEET_URL)
excel_data = load_excel(WORKBOOK_PATH)

# =====================================================
# 🤖 تهيئة المساعد القانوني
# =====================================================
def init_ai():
    try:
        ai = MiniLegalAI(WORKBOOK_PATH)
        ai.db = excel_data
        ai.build_tfidf_matrix()
        return ai
    except Exception as e:
        st.warning(f"⚠️ لم يتم تهيئة المساعد القانوني بالكامل: {e}")
        return None

if "ai_instance" not in st.session_state:
    st.session_state["ai_instance"] = init_ai()
ai = st.session_state["ai_instance"]

# =====================================================
# 🧮 تبويب الحاسبات
# =====================================================
def calculators_tab():
    section_header("🧮 الحاسبات القانونية", "🧮")
    calc_options = [
        "مكافأة نهاية الخدمة",
        "بدلات العمل الإضافي والليلي والعطلات الرسمية",
        "التعويض عن الإجازات غير المستغلة",
        "بدل النقل والسكن",
        "حساب الأجور الشهرية مع الخصومات",
        "استحقاقات الفصل التعسفي",
        "إجازة الحمل والولادة",
        "مكافأة الإجازات المرضية",
        "استحقاقات تغيير الوظيفة أو النقل الداخلي",
        "حاسبة الدوام الجزئي",
        "تعويض إصابات العمل"
    ]
    choice = st.selectbox("اختر الحاسبة:", calc_options)
    st.success(f"💡 تم اختيار الحاسبة: **{choice}**")

# =====================================================
# 📚 تبويب اعرف حقوقك والتزاماتك (بتصميم ذهبي)
# =====================================================
def rights_tab():
    section_header("📚 اعرف حقوقك والتزاماتك", "📚")
    st.markdown("""
    <style>
    .rights-card {
        background: linear-gradient(135deg, #FFD700, #D4AF37);
        color: #000;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .rights-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 10px 25px rgba(0,0,0,0.25);
    }
    .rights-title {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    ul {
        margin-top: 5px;
        padding-left: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="rights-card">
            <div class="rights-title">⚖️ حقوق العامل:</div>
            <ul>
                <li>مكافأة نهاية الخدمة</li>
                <li>الأجر الشهري وبدل العمل الإضافي</li>
                <li>بدل النقل والسكن</li>
                <li>الإجازات السنوية والمرضية</li>
                <li>إجازة الزواج أو الوفاة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="rights-card">
            <div class="rights-title">👩‍🍼 حقوق المرأة العاملة:</div>
            <ul>
                <li>إجازة الحمل والولادة</li>
                <li>الحق في الرضاعة</li>
                <li>عدم الفصل أثناء الحمل</li>
                <li>بيئة عمل آمنة ومناسبة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="rights-card">
            <div class="rights-title">📋 التزامات العامل:</div>
            <ul>
                <li>الالتزام بساعات الدوام</li>
                <li>المحافظة على أسرار المنشأة</li>
                <li>تنفيذ المهام الموكلة بدقة</li>
                <li>إشعار صاحب العمل عند الغياب</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="rights-card">
            <div class="rights-title">🏢 التزامات صاحب العمل:</div>
            <ul>
                <li>دفع الأجور في موعدها</li>
                <li>توفير بيئة عمل آمنة</li>
                <li>منح الإجازات القانونية</li>
                <li>تسجيل العامل في الضمان الاجتماعي</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# 📝 تبويب محاكي الشكوى
# =====================================================
def complaint_simulator_tab():
    section_header("📝 محاكي الشكوى", "📝")
    st.info("🧩 هذه الأداة تتيح لك محاكاة تقديم شكوى عمالية إلكترونيًا (قيد التطوير).")

# =====================================================
# 👷 صفحة العمال
# =====================================================
def workers_section():
    section_header("👷 قسم العمال", "👷")
    tabs = ["🧮 الحاسبات", "📚 اعرف حقوقك", "📝 محاكي الشكوى"]
    selected_tab = st.radio("اختر التبويب:", tabs, horizontal=True)
    if selected_tab == "🧮 الحاسبات":
        calculators_tab()
    elif selected_tab == "📚 اعرف حقوقك":
        rights_tab()
    elif selected_tab == "📝 محاكي الشكوى":
        complaint_simulator_tab()

# =====================================================
# 🏠 باقي الصفحات
# =====================================================
def employers_section():
    section_header("🏢 أصحاب العمل", "🏢")
    st.info("📊 أدوات وأدلة لأصحاب العمل (قيد التوسع).")

def inspectors_section():
    section_header("🕵️ المفتشون", "🕵️")
    st.info("🔍 أدوات التفتيش والتحقق قيد التطوير.")

def researchers_section():
    section_header("📖 الباحثون والمتدربون", "📖")
    st.info("📚 مواد تدريبية ومراجع قانونية.")

def settings_page():
    section_header("⚙️ الإعدادات", "⚙️")
    new_path = st.text_input("📁 مسار ملف Excel:", value=WORKBOOK_PATH)
    new_sheet = st.text_input("🗂️ رابط Google Sheet:", value=SHEET_URL)
    if st.button("💾 حفظ"):
        settings.settings["WORKBOOK_PATH"] = new_path
        settings.settings["SHEET_URL"] = new_sheet
        settings.save_settings()
        st.success("✅ تم حفظ الإعدادات بنجاح!")

# =====================================================
# 🏠 الصفحة الرئيسية
# =====================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

def show_home():
    CARD_GRADIENT = "linear-gradient(135deg, #FFD700, #D4AF37)"
    CARD_TEXT_COLOR = "#000000"
    ICON_PATH = "assets/icons/"
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background: {CARD_GRADIENT};
                border-radius:15px; color:{CARD_TEXT_COLOR}; margin-bottom:20px;">
        <h1>⚖️ {config.get('APP_NAME')}</h1>
        <p>الوصول السريع إلى أقسام المنصة الذكية</p>
    </div>
    """, unsafe_allow_html=True)
    categories = [
        {"label": "👷 العمال", "key": "workers", "icon": "workers.png"},
        {"label": "🏢 أصحاب العمل", "key": "employers", "icon": "employers.png"},
        {"label": "🕵️ المفتشون", "key": "inspectors", "icon": "inspectors.png"},
        {"label": "📖 الباحثون والمتدربون", "key": "researchers", "icon": "researchers.png"},
        {"label": "⚙️ الإعدادات", "key": "settings", "icon": "settings.png"}
    ]
    cols = st.columns(3)
    for idx, cat in enumerate(categories):
        with cols[idx % 3]:
            if st.button(cat["label"], key=f"btn_{cat['key']}"):
                st.session_state.current_page = cat["key"]

# =====================================================
# 🧭 نظام التنقل
# =====================================================
pages = {
    "home": show_home,
    "workers": workers_section,
    "employers": employers_section,
    "inspectors": inspectors_section,
    "researchers": researchers_section,
    "settings": settings_page
}
if st.session_state.current_page != "home" and st.button("⬅️ العودة"):
    st.session_state.current_page = "home"
else:
    pages[st.session_state.current_page]()

# =====================================================
# ⚖️ Footer
# =====================================================
st.markdown(f"<hr><center><small>{config.get('FOOTER', {}).get('TEXT')}</small></center>", unsafe_allow_html=True)