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
# 🏠 الصفحات الرئيسية
# =====================================================
def show_home():
    st.title(f"⚖️ {config.get('APP_NAME', 'منصة قانون العمل الأردني الذكية')}")
    st.markdown("منصة ذكية لتبسيط وفهم <b>قانون العمل الأردني</b>.", unsafe_allow_html=True)
    st.info("💡 هذه المنصة لأغراض التوعية القانونية فقط.")

# =====================================================
# 🧭 القائمة الجانبية
# =====================================================
menu_labels = [
    "🏠 الصفحة الرئيسية"
]

menu_icons = ["house"]

with st.sidebar:
    # تجاهل شعار logo.png إذا كان مفقود
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
    "🏠 الصفحة الرئيسية": show_home
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