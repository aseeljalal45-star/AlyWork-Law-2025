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
# 🧮 الحاسبات القانونية
# =====================================================
def calculators_tab():
    section_header("🧮 الحاسبات القانونية", "🧮")
    calc_options = [
        "حساب الأجور الشهرية",
        "التعويض عن الفصل التعسفي",
        "بدلات العمل الإضافي والليلي",
        "بدل النقل والسكن"
    ]
    choice = st.selectbox("اختر الحاسبة:", calc_options)
    st.success(f"💡 تم اختيار الحاسبة: **{choice}**")

# =====================================================
# 📚 الحقوق والالتزامات الخاصة بأصحاب العمل
# =====================================================
def rights_tab():
    section_header("📚 حقوق والتزامات صاحب العمل", "📚")
    st.markdown("""
    <style>
    .rights-card {background: linear-gradient(135deg,#FFD700,#D4AF37); color:#000; padding:20px;
        border-radius:20px; box-shadow:0px 5px 15px rgba(0,0,0,0.1); margin-bottom:20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;}
    .rights-card:hover {transform:translateY(-5px); box-shadow:0px 10px 25px rgba(0,0,0,0.25);}
    .rights-title {font-size:22px;font-weight:bold;margin-bottom:10px;}
    ul {margin-top:5px;padding-left:20px;}
    </style>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="rights-card"><div class="rights-title">⚖️ حقوق صاحب العمل:</div>
        <ul>
            <liالالتزام بالقوانين المحلية والعمل بموجب قانون العمل</li>
            <li>استلام تقارير ومطالبات العمال ومراجعتها</li>
            <li>تطبيق عقوبات مناسبة على المخالفين من الموظفين</li>
        </ul></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="rights-card"><div class="rights-title">📋 الالتزامات:</div>
        <ul>
            <li>دفع الأجور في مواعيدها</li>
            <li>تسجيل الموظفين في الضمان الاجتماعي</li>
            <li>توفير بيئة عمل آمنة وصحية</li>
            <li>الالتزام بالإجازات القانونية</li>
        </ul></div>""", unsafe_allow_html=True)

# =====================================================
# 📝 محاكي المخاطر القانونية لصاحب العمل
# =====================================================
def complaint_simulator_tab():
    section_header("📝 محاكي المخاطر القانونية", "📝")
    st.info("🧩 هذه الأداة تساعد صاحب العمل على تقييم المخاطر القانونية والتوصية بالإجراءات.")
    st.subheader("📌 بيانات الشركة")
    اسم_الشركة = st.text_input("اسم الشركة (اختياري)")
    عدد_الموظفين = st.number_input("عدد الموظفين:", min_value=0, step=1)
    نوع_المخاطر = st.selectbox("اختر نوع المخاطر:", [
        "تأخير دفع الأجور",
        "مخاطر الفصل التعسفي",
        "عدم تطبيق الضمان الاجتماعي",
        "انتهاكات أخرى"
    ])
    وصف_الحالة = st.text_area("صف الحالة باختصار:", "")
    if st.button("🔍 تحليل المخاطر"):
        توصية = "📌 يجب مراجعة القوانين واتخاذ الإجراءات القانونية المناسبة."
        st.subheader("📄 التقرير القانوني")
        st.markdown(f"""
        - **اسم الشركة:** {اسم_الشركة or "غير محدد"}
        - **عدد الموظفين:** {عدد_الموظفين}
        - **نوع المخاطر:** {نوع_المخاطر}
        - **وصف الحالة:** {وصف_الحالة or 'لا يوجد وصف'}
        - **التوصية:** {توصية}
        """)
        st.success("✅ التحليل تم بنجاح")

# =====================================================
# 🏛️ الجهات المختصة
# =====================================================
def complaints_places_tab():
    section_header("🏛️ الجهات المختصة", "🏛️")
    محافظة = st.selectbox("اختر المحافظة:", [
        "عمان", "إربد", "الزرقاء", "البلقاء", "الكرك", "معان",
        "الطفيلة", "المفرق", "مادبا", "جرش", "عجلون", "العقبة"
    ])
    الجهات = {
        "عمان": {"الجهة":"مديرية العمل – عمان","العنوان":"عمان، شارع عيسى الناوري 11","الهاتف":"06‑5802666","البريد":"info@mol.gov.jo","الموقع":"http://www.mol.gov.jo"},
        "إربد": {"الجهة":"مديرية العمل – إربد","العنوان":"إربد، الأردن","الهاتف":"06‑xxxxxxx","البريد":"irbid@mol.gov.jo","الموقع":"http://www.mol.gov.jo/irbid"},
    }
    info = الجهات.get(محافظة)
    if info:
        st.markdown(f"""
        <div style="background:#f0f0f0;padding:15px;border-radius:15px;margin-bottom:10px;">
        <b>{info['الجهة']}</b><br>
        العنوان: {info['العنوان']}<br>
        الهاتف: {info['الهاتف']}<br>
        البريد: {info['البريد']}<br>
        الموقع: <a href="{info['الموقع']}" target="_blank">{info['الموقع']}</a>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ لا توجد بيانات متوفّرة لهذه المحافظة بعد.")

# =====================================================
# 👥 الأقسام حسب الفئة
# =====================================================
def section_tabs(section_name):
    tabs = ["🧮 الحاسبات", "📚 الحقوق", "📝 المحاكي", "🏛️ الجهات المختصة"]
    selected_tab = st.radio(f"اختر التبويب في {section_name}:", tabs, horizontal=True)
    if selected_tab == "🧮 الحاسبات":
        calculators_tab()
    elif selected_tab == "📚 الحقوق":
        rights_tab()
    elif selected_tab == "📝 المحاكي":
        complaint_simulator_tab()
    elif selected_tab == "🏛️ الجهات المختصة":
        complaints_places_tab()

def workers_section(): section_tabs("قسم العمال")
def owners_section(): section_tabs("قسم أصحاب العمل")
def inspectors_section(): section_tabs("قسم المفتشون")
def researchers_section(): section_tabs("قسم الباحثون")
def trainees_section(): section_tabs("قسم المتدربون")

# =====================================================
# 🏠 الصفحة الرئيسية
# =====================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

def show_home():
    CARD_GRADIENT = "linear-gradient(135deg,#FFD700,#D4AF37)"
    CARD_TEXT_COLOR = "#000000"
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background: {CARD_GRADIENT};
                border-radius:15px; color:{CARD_TEXT_COLOR}; margin-bottom:20px;">
        <h1>⚖️ {config.get('APP_NAME')}</h1>
        <p>الوصول السريع إلى أقسام المنصة الذكية</p>
    </div>
    """, unsafe_allow_html=True)
    for sec_name, sec_func in [
        ("👷 العمال", "workers"),
        ("🏢 أصحاب العمل", "owners"),
        ("🔍 المفتشون", "inspectors"),
        ("📖 الباحثون", "researchers"),
        ("🏫 المتدربون", "trainees")
    ]:
        if st.button(sec_name):
            st.session_state.current_page = sec_func

# =====================================================
# 🧭 نظام التنقل
# =====================================================
pages = {
    "home": show_home,
    "workers": workers_section,
    "owners": owners_section,
    "inspectors": inspectors_section,
    "researchers": researchers_section,
    "trainees": trainees_section,
}

if st.session_state.current_page != "home" and st.button("⬅️ العودة"):
    st.session_state.current_page = "home"
else:
    pages[st.session_state.current_page]()

# =====================================================
# ⚖️ Footer
# =====================================================
st.markdown(f"<hr><center><small>{config.get('FOOTER', {}).get('TEXT')}</small></center>", unsafe_allow_html=True)