import streamlit as st
from streamlit_option_menu import option_menu
import os, pandas as pd
from helpers.mini_ai_smart import MiniLegalAI
from helpers.settings_manager import SettingsManager
from helpers.ui_components import message_bubble, section_header, info_card
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import plotly.express as px

# ==============================
# ⚙️ Initialize Settings
# ==============================
settings = SettingsManager()
config = st.session_state["config"]

# ==============================
# ⚙️ Page config
# ==============================
st.set_page_config(
    page_title=config.get("APP_NAME", "منصة قانون العمل الأردني الذكية"),
    page_icon="⚖️",
    layout="wide"
)

# ==============================
# 🌈 Load official CSS
# ==============================
def load_official_css():
    css_file = "assets/styles_official.css"  # أنشئ هذا الملف لتحتوي الألوان الرسمية
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_official_css()

# ==============================
# 📊 Load Google Sheet safely
# ==============================
def sheet_to_csv_url(sheet_url):
    import re
    if "docs.google.com/spreadsheets" in sheet_url and "export?format=csv" not in sheet_url:
        m = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
        if m: return f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=csv"
    return sheet_url

SHEET_URL = settings.get("SHEET_URL", config.get("SHEET_URL", ""))

@st.cache_data(ttl=config.get("CACHE", {}).get("TTL_SECONDS", 600))
def load_google_sheets(url):
    if not url:
        st.info("🗂️ لم يتم تحديد رابط Google Sheet بعد.")
        return pd.DataFrame()
    url = sheet_to_csv_url(url)
    with st.spinner("⏳ جاري تحميل البيانات..."):
        try:
            return pd.read_csv(url)
        except Exception as e:
            st.error(f"⚠️ خطأ أثناء تحميل Google Sheet: {e}")
            return pd.DataFrame()

data = load_google_sheets(SHEET_URL)

# ==============================
# 🤖 Initialize MiniLegalAI
# ==============================
workbook_path = settings.get("WORKBOOK_PATH", config.get("WORKBOOK_PATH"))

@st.cache_data(ttl=config.get("CACHE", {}).get("TTL_SECONDS", 600))
def safe_load_excel(path):
    if not os.path.exists(path):
        st.warning(f"⚠️ ملف Excel غير موجود: {path}")
        return pd.DataFrame(columns=['المادة','القسم','النص','مثال'])
    try:
        df = pd.read_excel(path, engine='openpyxl')
        df.fillna("", inplace=True)
        return df
    except:
        return pd.DataFrame(columns=['المادة','القسم','النص','مثال'])

excel_data = safe_load_excel(workbook_path)

if os.path.exists(workbook_path):
    try:
        ai = MiniLegalAI(workbook_path)
        ai.db = excel_data
        ai.build_tfidf_matrix()
    except:
        ai = None
else:
    ai = None

# ==============================
# 🧠 AI Assistant
# ==============================
def show_ai_assistant():
    if not config.get("AI", {}).get("ENABLE", True) or ai is None:
        return
    section_header("🤖 المساعد القانوني الذكي", "🤖")
    query = st.text_input("💬 اكتب سؤالك هنا:")
    if query:
        answer, reference, example = ai.advanced_search(query)
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        st.session_state["chat_history"].append({"user": query, "ai": answer})
        max_history = config.get("AI", {}).get("MAX_HISTORY", 20)
        for chat in st.session_state["chat_history"][-max_history:]:
            message_bubble("User", chat["user"], is_user=True)
            message_bubble("AI", chat["ai"], is_user=False)
        st.markdown(f"**📜 نص القانون:** {reference}")
        st.markdown(f"**💡 مثال تطبيقي:** {example}")

# ==============================
# 📈 Data Table
# ==============================
def show_data_table(df):
    if df.empty:
        st.warning("⚠️ لا توجد بيانات للعرض.")
        return
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(editable=True, filter=True)
    AgGrid(df, gridOptions=gb.build(), enable_enterprise_modules=False, height=400)

# ==============================
# 📊 Statistics
# ==============================
def show_statistics(df):
    if df.empty: return
    st.markdown("### 📊 إحصائيات سريعة")
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد المواد القانونية", len(df))
    col2.metric("عدد التعديلات", df['المادة'].nunique() if 'المادة' in df.columns else 0)
    col3.metric("عدد الأقسام القانونية", df['القسم'].nunique() if 'القسم' in df.columns else 0)
    if 'القسم' in df.columns:
        counts = df['القسم'].value_counts()
        fig = px.pie(values=counts.values, names=counts.index, title="نسبة المواد حسب القسم", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

# ==============================
# 💡 Smart Recommender
# ==============================
from helpers.recommender import smart_recommender

# ==============================
# 🏠 Pages
# ==============================
def show_home():
    st.title(f"⚖️ {config.get('APP_NAME')}")
    st.markdown("منصة ذكية لتبسيط وفهم <b>قانون العمل الأردني</b>.", unsafe_allow_html=True)
    st.info("⚠️ المنصة لأغراض التوعية القانونية فقط.")
    show_data_table(data.head(10))
    show_statistics(data)
    show_ai_assistant()
    smart_recommender("العمال", n=config.get("RECOMMENDER", {}).get("MAX_CARDS", 6))

def workers_section(): section_header("👷 قسم العمال", "👷"); show_ai_assistant(); smart_recommender("العمال")
def employers_section(): section_header("🏢 قسم أصحاب العمل", "🏢"); show_ai_assistant(); smart_recommender("اصحاب العمل")
def inspectors_section(): section_header("🕵️ قسم المفتشين", "🕵️"); show_ai_assistant(); smart_recommender("مفتشو العمل")
def researchers_section(): section_header("📖 قسم الباحثين والمتدربين", "📖"); show_ai_assistant(); smart_recommender("الباحثون والمتدربون")
def settings_page(): section_header("⚙️ الإعدادات", "⚙️"); st.write("يمكن تعديل الإعدادات من هنا")

# ==============================
# ⚙️ Sidebar
# ==============================
menu_items_labels = ["🏠 الصفحة الرئيسية", "👷 العمال", "🏢 أصحاب العمل",
                     "🕵️ مفتشو العمل", "📖 الباحثون والمتدربون", "⚙️ الإعدادات"]
menu_items_icons  = ["house", "people", "briefcase", "search", "book", "gear"]

with st.sidebar:
    choice = option_menu(
        "القائمة الرئيسية",
        menu_items_labels,
        icons=menu_items_icons,
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

if choice:
    pages.get(choice, lambda: st.error("صفحة غير متاحة"))()
else:
    show_home()

# ==============================
# ⏰ Footer
# ==============================
st.markdown(
    f"<hr><center><small>{config.get('FOOTER', {}).get('TEXT')}</small></center>",
    unsafe_allow_html=True
)