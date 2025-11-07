import streamlit as st
from streamlit_option_menu import option_menu
import os, pandas as pd
from helpers.mini_ai_smart import MiniLegalAI
from helpers.settings_manager import SettingsManager
from helpers.ui_components import message_bubble, section_header, info_card
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import plotly.express as px

# =====================================================
# ⚙️ تهيئة الإعدادات العامة
# =====================================================
settings = SettingsManager()
config = st.session_state["config"]

st.set_page_config(
    page_title=config.get("APP_NAME", "منصة قانون العمل الأردني الذكية"),
    page_icon="⚖️",
    layout="wide"
)

# =====================================================
# 🌈 تحميل ملف CSS الرسمي
# =====================================================
def load_official_css():
    css_file = "assets/styles_official.css"
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ ملف CSS الرسمي غير موجود: assets/styles_official.css")

load_official_css()

# =====================================================
# 🧮 تحميل Google Sheets بأمان
# =====================================================
def sheet_to_csv_url(sheet_url):
    import re
    if "docs.google.com/spreadsheets" in sheet_url and "export?format=csv" not in sheet_url:
        m = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
        if m:
            return f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=csv"
    return sheet_url

SHEET_URL = settings.get("SHEET_URL", config.get("SHEET_URL", ""))

@st.cache_data(ttl=config.get("CACHE", {}).get("TTL_SECONDS", 600))
def load_google_sheets(url):
    if not url:
        st.warning("🗂️ لم يتم تحديد رابط Google Sheet بعد.")
        return pd.DataFrame()
    url = sheet_to_csv_url(url)
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.warning(f"⚠️ خطأ أثناء تحميل Google Sheet: {e}")
        return pd.DataFrame()

data = load_google_sheets(SHEET_URL)

# =====================================================
# 📘 تحميل ملف Excel للذكاء القانوني
# =====================================================
workbook_path = settings.get("WORKBOOK_PATH", config.get("WORKBOOK_PATH", "AlyWork_Law_Pro_v2025.xlsx"))

@st.cache_data(ttl=config.get("CACHE", {}).get("TTL_SECONDS", 600))
def safe_load_excel(path):
    if not os.path.exists(path):
        st.warning(f"⚠️ ملف Excel غير موجود: {path}")
        return pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال'])
    try:
        df = pd.read_excel(path, engine='openpyxl')
        expected_cols = ['المادة', 'القسم', 'النص', 'مثال']
        for col in expected_cols:
            if col not in df.columns:
                st.warning(f"⚠️ العمود '{col}' غير موجود في ملف Excel.")
                df[col] = ""
        df.fillna("", inplace=True)
        return df
    except Exception as e:
        st.warning(f"⚠️ خطأ أثناء قراءة Excel: {e}")
        return pd.DataFrame(columns=['المادة', 'القسم', 'النص', 'مثال'])

excel_data = safe_load_excel(workbook_path)

if os.path.exists(workbook_path):
    try:
        ai = MiniLegalAI(workbook_path)
        ai.db = excel_data
        ai.build_tfidf_matrix()
    except Exception as e:
        st.warning(f"⚠️ لم يتم تهيئة المساعد القانوني بالكامل: {e}")
        ai = None
else:
    ai = None

# =====================================================
# 🤖 واجهة المساعد القانوني الذكي
# =====================================================
def show_ai_assistant():
    if not config.get("AI", {}).get("ENABLE", True) or ai is None:
        st.info("🤖 المساعد غير مفعل حالياً.")
        return

    section_header("🤖 المساعد القانوني الذكي", "🤖")
    query = st.text_input("💬 اكتب سؤالك القانوني هنا:")
    if query:
        answer, reference, example = ai.advanced_search(query)
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        st.session_state["chat_history"].append({"user": query, "ai": answer})
        max_history = config.get("AI", {}).get("MAX_HISTORY", 20)

        for chat in st.session_state["chat_history"][-max_history:]:
            message_bubble("👤 المستخدم", chat["user"], is_user=True)
            message_bubble("🤖 المساعد", chat["ai"], is_user=False)

        if reference:
            st.markdown(f"**📜 نص القانون:** {reference}")
        if example:
            st.markdown(f"**💡 مثال تطبيقي:** {example}")

# =====================================================
# 💡 Smart Recommender
# =====================================================
ICON_PATH = config.get("UI", {}).get("ICON_PATH", "assets/icons/")
MAX_CARDS = config.get("RECOMMENDER", {}).get("MAX_CARDS", 6)

def get_recommendations_data():
    data = {
        "العمال": [
            {"العنوان": "احسب مكافأة نهاية الخدمة", "الوصف": "استخدم الحاسبة لتقدير مستحقاتك.", "النوع": "حاسبة", "link": "#", "icon": "🧮", "img": f"{ICON_PATH}service_end.png"},
            {"العنوان": "راجع حقوقك الأساسية", "الوصف": "تعرف على حقوقك وفق القانون الأردني.", "النوع": "توعية", "link": "#", "icon": "📚", "img": f"{ICON_PATH}rights.png"},
            {"العنوان": "اطلع على سوابق قضائية", "الوصف": "أحكام مشابهة لحالتك.", "النوع": "قانوني", "link": "#", "icon": "⚖️", "img": f"{ICON_PATH}legal_case.png"},
            {"العنوان": "تطبيقات عملية", "الوصف": "أمثلة تطبيقية للمواد القانونية.", "النوع": "تعليمي", "link": "#", "icon": "💡", "img": f"{ICON_PATH}practice.png"}
        ],
        "اصحاب العمل": [
            {"العنوان": "حاسبة تكاليف الموظفين", "الوصف": "تقدير التزامات الأجور والضرائب.", "النوع": "حاسبة", "link": "#", "icon": "🧮", "img": f"{ICON_PATH}service_end.png"},
            {"العنوان": "الامتثال القانوني", "الوصف": "راجع التزاماتك وفق القانون الأردني.", "النوع": "امتثال", "link": "#", "icon": "⚖️", "img": f"{ICON_PATH}legal_case.png"}
        ],
        "مفتشو العمل": [
            {"العنوان": "نموذج تقرير تفتيش", "الوصف": "نماذج جاهزة للتوثيق.", "النوع": "نموذج", "link": "#", "icon": "📄", "img": f"{ICON_PATH}practice.png"}
        ],
        "الباحثون والمتدربون": [
            {"العنوان": "استعراض السوابق القانونية", "الوصف": "اطلع على الحالات السابقة.", "النوع": "بحث", "link": "#", "icon": "🔍", "img": f"{ICON_PATH}legal_case.png"}
        ]
    }
    return data

def smart_recommender(role_label="العمال", n=None):
    recommendations = get_recommendations_data().get(role_label, [])
    if not recommendations:
        st.info("ℹ️ لا توجد توصيات حالياً لهذه الفئة.")
        return

    section_header("💡 اقتراحات ذكية لك", "💡")
    n = n or MAX_CARDS
    cols = st.columns(3)
    type_styles = {
        "حاسبة": "linear-gradient(135deg, #3b82f6, #1d4ed8)",
        "توعية": "linear-gradient(135deg, #10b981, #059669)",
        "قانوني": "linear-gradient(135deg, #6366f1, #4338ca)",
        "تعليمي": "linear-gradient(135deg, #f59e0b, #d97706)",
        "امتثال": "linear-gradient(135deg, #9333ea, #7e22ce)",
        "مالي": "linear-gradient(135deg, #ec4899, #db2777)",
        "مرجع": "linear-gradient(135deg, #14b8a6, #0d9488)",
        "نموذج": "linear-gradient(135deg, #f97316, #ea580c)",
        "بحث": "linear-gradient(135deg, #22c55e, #16a34a)"
    }

    for idx, rec in enumerate(recommendations[:n]):
        with cols[idx % len(cols)]:
            style = type_styles.get(rec['النوع'], "linear-gradient(135deg, #9ca3af, #6b7280)")
            st.markdown(
                f"""
                <div style="background: {style};
                            border-radius:15px;
                            padding:18px;
                            margin:8px;
                            box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
                            text-align:center;
                            color:white;">
                    <img src='{rec['img']}' alt='icon' width='50px' style='margin-bottom:10px;'/>
                    <h4 style='margin-bottom:5px;'>{rec['icon']} {rec['العنوان']}</h4>
                    <p style='font-size:14px; opacity:0.9;'>{rec['الوصف']}</p>
                    <a href='{rec['link']}' target='_blank' style='color:#fff; text-decoration:underline;'>اضغط هنا للتفاصيل</a>
                </div>
                """,
                unsafe_allow_html=True
            )

# =====================================================
# 🏠 الصفحات الرئيسية
# =====================================================
def show_home():
    st.title(f"⚖️ {config.get('APP_NAME', 'منصة قانون العمل الأردني الذكية')}")
    st.markdown("منصة ذكية لتبسيط وفهم <b>قانون العمل الأردني</b>.", unsafe_allow_html=True)
    st.info("💡 هذه المنصة لأغراض التوعية القانونية فقط.")
    show_ai_assistant()
    smart_recommender("العمال")

def workers_section():
    section_header("👷 قسم العمال", "👷")
    show_ai_assistant()
    smart_recommender("العمال")

def employers_section():
    section_header("🏢 قسم أصحاب العمل", "🏢")
    show_ai_assistant()
    smart_recommender("اصحاب العمل")

def inspectors_section():
    section_header("🕵️ قسم المفتشين", "🕵️")
    show_ai_assistant()
    smart_recommender("مفتشو العمل")

def researchers_section():
    section_header("📖 قسم الباحثين والمتدربين", "📖")
    show_ai_assistant()
    smart_recommender("الباحثون والمتدربون")

def settings_page():
    section_header("⚙️ الإعدادات", "⚙️")
    st.write("يمكنك تعديل الإعدادات من هنا.")
    new_path = st.text_input("📁 مسار ملف Excel:", value=workbook_path)
    if st.button("💾 حفظ"):
        settings.settings["WORKBOOK_PATH"] = new_path
        with open(settings.path, "w", encoding="utf-8") as f:
            import json
            json.dump(settings.settings, f, indent=4, ensure_ascii=False)
        st.success("✅ تم حفظ الإعدادات بنجاح!")

# =====================================================
# 🧭 القائمة الجانبية
# =====================================================
menu_labels = [
    "🏠 الصفحة الرئيسية",
    "👷 العمال",
    "🏢 أصحاب العمل",
    "🕵️ مفتشو العمل",
    "📖 الباحثون والمتدربون",
    "⚙️ الإعدادات"
]
menu_icons = ["house", "people", "briefcase", "search", "book", "gear"]

with st.sidebar:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=180)
    else:
        st.info("ℹ️ شعار المنصة غير موجود.")

    choice = option_menu(
        "القائمة الرئيسية",
        menu_labels,
        icons=menu_icons,
        default_index=0
    )

pages = {
    "🏠 الصفحة الرئيسية": show_home,
    "👷 العمال": workers_section,
    "🏢 أصحاب العمل": employers_section,
    "🕵️ مفتشو العمل": inspectors_section,
    "📖 الباحثون والمتدربون": researchers_section,
    "⚙️ الإعدادات": settings_page
}

if choice in pages:
    pages[choice]()
else:
    show_home()

# =====================================================
# 🕒 تذييل رسمي
# =====================================================
st.markdown(
    f"<hr><center><small>{config.get('FOOTER', {}).get('TEXT', 'AlyWork Law Pro © 2025 — جميع الحقوق محفوظة 🇯🇴')}</small></center>",
    unsafe_allow_html=True
)