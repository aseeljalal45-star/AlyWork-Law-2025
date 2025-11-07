import streamlit as st
from streamlit_option_menu import option_menu
import os, pandas as pd
from helpers.mini_ai_smart import MiniLegalAI
from helpers.settings_manager import SettingsManager
from helpers.ui_components import message_bubble, section_header, info_card
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import plotly.express as px
from helpers.recommender import smart_recommender

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
        df.fillna("", inplace=True)
        return df
    except Exception as e:
        st.error(f"⚠️ خطأ أثناء قراءة Excel: {e}")
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
# 📊 عرض الجدول والإحصائيات
# =====================================================
def show_data_table(df):
    if df.empty:
        st.warning("⚠️ لا توجد بيانات متاحة.")
        return
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(editable=False, filter=True)
    AgGrid(df, gridOptions=gb.build(), enable_enterprise_modules=False, height=400)

def show_statistics(df):
    if df.empty:
        return
    st.markdown("### 📊 إحصائيات سريعة")
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد المواد القانونية", len(df))
    col2.metric("عدد الفصول", df['القسم'].nunique() if 'القسم' in df.columns else 0)
    col3.metric("عدد التعديلات", df['المادة'].nunique() if 'المادة' in df.columns else 0)

    if 'القسم' in df.columns:
        counts = df['القسم'].value_counts()
        fig = px.pie(values=counts.values, names=counts.index, title="نسبة المواد حسب القسم", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 🏠 الصفحات الرئيسية
# =====================================================
def show_home():
    st.title(f"⚖️ {config.get('APP_NAME', 'منصة قانون العمل الأردني الذكية')}")
    st.markdown("منصة ذكية لتبسيط وفهم <b>قانون العمل الأردني</b>.", unsafe_allow_html=True)
    st.info("💡 هذه المنصة لأغراض التوعية القانونية فقط.")
    show_data_table(data.head(10))
    show_statistics(data)
    show_ai_assistant()
    smart_recommender("العمال", n=config.get("RECOMMENDER", {}).get("MAX_CARDS", 6))

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
    st.image("assets/logo.png", width=180)
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