import streamlit as st
from streamlit_option_menu import option_menu
import os, datetime, json, pandas as pd
from helpers.mini_ai_smart import MiniLegalAI
from helpers.settings_manager import SettingsManager
from helpers.ui_components import message_bubble, section_header, info_card
from recommender import smart_recommender
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import plotly.express as px

# ==============================
# ⚙️ تحميل الإعدادات من config.json
# ==============================
CONFIG_PATH = "config.json"

def load_config():
    """تحميل ملف الإعدادات أو إنشاء إعداد افتراضي إن لم يكن موجودًا"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        st.warning("⚠️ لم يتم العثور على ملف config.json — سيتم استخدام إعدادات افتراضية.")
        return {
            "APP_NAME": "منصة قانون العمل الأردني الذكية",
            "THEME": "فاتح",
            "UI": {},
            "AI": {"ENABLE": True, "MAX_HISTORY": 10},
            "SIDEBAR": {"MENU_ITEMS": [
                {"label": "🏠 الرئيسية", "icon": "house", "func": "show_home"},
                {"label": "👷 العمال", "icon": "person", "func": "workers_section"},
                {"label": "🏢 أصحاب العمل", "icon": "building", "func": "employers_section"},
                {"label": "🕵️ مفتشو العمل", "icon": "search", "func": "inspectors_section"},
                {"label": "📖 الباحثون والمتدربون", "icon": "book", "func": "researchers_section"},
                {"label": "⚙️ الإعدادات", "icon": "gear", "func": "settings_page"}
            ]},
            "FOOTER": {"TEXT": "© 2025 AlyWork Law Pro — جميع الحقوق محفوظة."}
        }

config = load_config()
settings = SettingsManager()

# ==============================
# ⚙️ إعداد الصفحة العامة
# ==============================
st.set_page_config(
    page_title=config.get("APP_NAME", "منصة قانون العمل الأردني الذكية"),
    page_icon="⚖️",
    layout="wide"
)

# ==============================
# 🌈 Theme ديناميكي
# ==============================
def load_css(theme=None):
    """تحميل ملف CSS حسب الثيم (فاتح/غامق)"""
    if theme is None:
        theme = config.get("THEME", "فاتح")
    ui = config.get("UI", {})
    css_file = ui.get("STYLES_LIGHT") if theme == "فاتح" else ui.get("STYLES_DARK")
    if css_file and os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.write("")  # صامت بدون خطأ

load_css(settings.get("THEME", config.get("THEME", "فاتح")))

# ==============================
# 📊 تحميل بيانات Google Sheets
# ==============================
def sheet_to_csv_url(sheet_url):
    """تحويل رابط Google Sheet إلى رابط CSV مباشر"""
    if "docs.google.com/spreadsheets" in sheet_url and "export?format=csv" not in sheet_url:
        import re
        m = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
        if m:
            sheet_id = m.group(1)
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    return sheet_url

SHEET_URL = config.get("SHEET_URL", "")

@st.cache_data(ttl=config.get("CACHE", {}).get("TTL_SECONDS", 600))
def load_google_sheets(url):
    try:
        if not url:
            st.info("🗂️ لم يتم تحديد رابط Google Sheet بعد.")
            return pd.DataFrame()
        url = sheet_to_csv_url(url)
        with st.spinner("⏳ جاري تحميل البيانات..."):
            df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل البيانات: {e}")
        return pd.DataFrame()

data = load_google_sheets(SHEET_URL)

# ==============================
# 🤖 إعداد المساعد الذكي
# ==============================
workbook_path = os.getenv("WORKBOOK_PATH", config.get("WORKBOOK_PATH", "AlyWork_Law_Pro_v2025_v24_ColabStreamlitReady.xlsx"))
if not os.path.exists(workbook_path):
    st.warning("⚠️ ملف Excel الخاص بـ MiniLegalAI غير موجود. سيتم تفعيل المساعد فقط بعد رفع الملف.")
ai = MiniLegalAI(workbook_path) if os.path.exists(workbook_path) else None

# ==============================
# 🧠 المساعد القانوني الذكي
# ==============================
def show_ai_assistant():
    if not config.get("AI", {}).get("ENABLE", True):
        return
    section_header("🤖 المساعد القانوني الذكي", "🤖")
    query = st.text_input("💬 اكتب سؤالك هنا:")
    if query and ai:
        answer, reference, example = ai.advanced_search(query)
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        st.session_state.chat_history.append({"user": query, "ai": answer})
        for chat in st.session_state.chat_history[-config.get("AI", {}).get("MAX_HISTORY", 20):]:
            message_bubble("User", chat['user'], is_user=True)
            message_bubble("AI", chat['ai'], is_user=False)
        st.markdown(f"**📜 نص القانون:** {reference}")
        st.markdown(f"**💡 مثال تطبيقي:** {example}")
    elif query and not ai:
        st.error("⚠️ المساعد غير مفعل حالياً لعدم توفر ملف Excel.")

# ==============================
# 📈 عرض البيانات بشكل تفاعلي
# ==============================
def show_data_table(df):
    if df.empty:
        st.warning("⚠️ لا توجد بيانات للعرض.")
        return
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(editable=True, filter=True)
    grid_options = gb.build()
    AgGrid(df, gridOptions=grid_options, enable_enterprise_modules=False, height=400)

# ==============================
# 📊 Charts و Metrics
# ==============================
def show_statistics(df):
    st.markdown("### 📊 إحصائيات سريعة")
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد المواد القانونية", len(df))
    col2.metric("عدد التعديلات", df['المادة'].nunique() if 'المادة' in df.columns else 0)
    col3.metric("عدد الأقسام القانونية", df['القسم'].nunique() if 'القسم' in df.columns else 0)
    if 'القسم' in df.columns:
        section_counts = df['القسم'].value_counts()
        fig = px.pie(values=section_counts.values, names=section_counts.index,
                     title="نسبة المواد حسب القسم", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

# ==============================
# 🏠 الصفحة الرئيسية
# ==============================
def show_home():
    st.title(f"⚖️ {config.get('APP_NAME', 'منصة قانون العمل الأردني الذكية')}")
    st.markdown(f"""
    منصة ذكية لتبسيط وفهم <b>قانون العمل الأردني لعام 1996</b>
    وتعديلاته حتى <b>2024</b>.
    """, unsafe_allow_html=True)
    st.info("⚠️ المنصة لأغراض التوعية القانونية فقط ولا تُغني عن الاستشارة القانونية.")
    st.markdown("---")

    sections = config.get("SIDEBAR", {}).get("MENU_ITEMS", [])
    cols = st.columns(3)
    for i, section in enumerate(sections[:-1]):  # تجاهل الإعدادات
        with cols[i % 3]:
            if st.button(f"{section['icon']} {section['label']}", key=section['label']):
                func_name = section.get('func')
                if func_name in globals() and callable(globals()[func_name]):
                    globals()[func_name]()

    show_data_table(data.head(10))
    show_statistics(data)

# ==============================
# 👷 العمال
# ==============================
def workers_section():
    section_header("👷 العمال", "👷")
    info_card("حقوق العامل", "الأجر، الإجازات، مكافأة نهاية الخدمة، بيئة عمل آمنة.")
    info_card("واجبات العامل", "الالتزام بالقوانين الداخلية واحترام النظام.")
    tabs = st.tabs(["مكافأة نهاية الخدمة", "الإجازات", "العمل الإضافي"])
    for tab in tabs:
        with tab:
            st.markdown(f"🛠️ أداة: {tab.title()}")
    show_ai_assistant()
    smart_recommender("العمال", n=config.get("RECOMMENDER", {}).get("MAX_CARDS", 6))

# ==============================
# 🏢 أصحاب العمل
# ==============================
def employers_section():
    section_header("🏢 أصحاب العمل", "🏢")
    info_card("حقوق صاحب العمل", "إدارة المنشأة ضمن القانون وتنظيم العقود.")
    info_card("الالتزامات", "دفع الأجور، تطبيق أنظمة السلامة، توثيق العقود.")
    tabs = st.tabs(["تكاليف الموظف", "التزامات الضمان", "الفصل القانوني"])
    for tab in tabs:
        with tab:
            st.markdown(f"🛠️ أداة: {tab.title()}")
    show_ai_assistant()
    smart_recommender("اصحاب العمل", n=config.get("RECOMMENDER", {}).get("MAX_CARDS", 6))

# ==============================
# 🕵️ مفتشو العمل
# ==============================
def inspectors_section():
    section_header("🕵️ مفتشو العمل", "🕵️")
    info_card("المهام", "مراقبة تطبيق أحكام القانون وضمان العدالة في بيئة العمل.")
    tabs = st.tabs(["دوري", "بناء على شكوى", "طارئ"])
    for tab in tabs:
        with tab:
            st.markdown(f"🛠️ نوع التفتيش: {tab.title()}")
    show_ai_assistant()
    smart_recommender("مفتشو العمل", n=config.get("RECOMMENDER", {}).get("MAX_CARDS", 6))

# ==============================
# 📖 الباحثون والمتدربون
# ==============================
def researchers_section():
    section_header("📖 الباحثون والمتدربون", "📖")
    tabs = st.tabs(["تحليل التعديلات", "اختبار قانوني", "استعراض السوابق"])
    for tab in tabs:
        with tab:
            st.markdown(f"🛠️ نوع التحليل: {tab.title()}")
    show_ai_assistant()
    smart_recommender("الباحثون والمتدربون", n=config.get("RECOMMENDER", {}).get("MAX_CARDS", 6))

# ==============================
# ⚙️ الإعدادات
# ==============================
def settings_page():
    section_header("⚙️ الإعدادات", "⚙️")
    theme = st.radio("اختر النمط:", ["فاتح", "غامق"], index=0 if settings.get("THEME", "فاتح")=="فاتح" else 1)
    lang = st.selectbox("اختر اللغة:", ["العربية", "English"], index=0 if settings.get("LANG", "ar")=="ar" else 1)
    settings.set("THEME", theme)
    settings.set("LANG", lang)
    load_css(theme)
    st.success("✅ تم حفظ الإعدادات.")

# ==============================
# 🧭 القائمة الجانبية (محسّنة وآمنة)
# ==============================
menu_items = config.get("SIDEBAR", {}).get("MENU_ITEMS", [])
labels = [item.get('label', 'غير معروف') for item in menu_items]
icons = [item.get('icon', '') for item in menu_items]

with st.sidebar:
    if labels:
        choice = option_menu("القائمة الرئيسية", labels, icons=icons, default_index=0)
    else:
        st.warning("لم يتم إعداد عناصر الشريط الجانبي في config.json.")
        choice = None

pages = {}
for item in menu_items:
    label = item.get('label')
    func_name = item.get('func')
    if func_name and func_name in globals() and callable(globals()[func_name]):
        pages[label] = globals()[func_name]
    else:
        pages[label] = lambda label=label, fn=func_name: st.warning(f"الصفحة '{label}' غير مُفعّلة. func: {fn}")

if choice:
    pages.get(choice, lambda: st.error("صفحة غير متاحة"))()
else:
    show_home()

# ==============================
# ⏰ Footer
# ==============================
st.markdown(
    f"<hr><center><small>{config.get('FOOTER', {}).get('TEXT', f'© {datetime.datetime.now().year} AlyWork Law Pro — جميع الحقوق محفوظة.')}</small></center>",
    unsafe_allow_html=True
)