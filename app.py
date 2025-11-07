import streamlit as st
import os, pandas as pd
from helpers.mini_ai_smart import MiniLegalAI
from helpers.settings_manager import SettingsManager
from helpers.ui_components import message_bubble, section_header, info_card
import plotly.express as px

# =====================================================
# ⚙️ إعدادات عامة
# =====================================================
settings = SettingsManager()
config = st.session_state["config"]

st.set_page_config(
    page_title=config.get("APP_NAME", "منصة قانون العمل الأردني الذكية"),
    page_icon="⚖️",
    layout="wide"
)

# =====================================================
# 🌈 تحميل CSS رسمي
# =====================================================
def load_official_css():
    css_file = "assets/styles_official.css"
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.info("ℹ️ ملف CSS الرسمي غير موجود: assets/styles_official.css")
load_official_css()

# =====================================================
# 🧮 تحميل Google Sheet و Excel
# =====================================================
def sheet_to_csv_url(sheet_url):
    import re
    if "docs.google.com/spreadsheets" in sheet_url and "export?format=csv" not in sheet_url:
        m = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
        if m:
            return f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=csv"
    return sheet_url

SHEET_URL = settings.get("SHEET_URL", config.get("SHEET_URL"))
workbook_path = settings.get("WORKBOOK_PATH", config.get("WORKBOOK_PATH"))

@st.cache_data(ttl=config.get("CACHE", {}).get("TTL_SECONDS", 600))
def load_google_sheets(url):
    if not url:
        st.info("ℹ️ لم يتم تحديد رابط Google Sheet بعد.")
        return pd.DataFrame()
    url = sheet_to_csv_url(url)
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.warning(f"⚠️ خطأ أثناء تحميل Google Sheet: {e}")
        return pd.DataFrame()

data = load_google_sheets(SHEET_URL)

@st.cache_data(ttl=config.get("CACHE", {}).get("TTL_SECONDS", 600))
def safe_load_excel(path):
    expected_cols = ['المادة', 'القسم', 'النص', 'مثال']
    if not os.path.exists(path):
        st.info(f"ℹ️ ملف Excel غير موجود: {path}. سيتم إنشاء DataFrame افتراضي.")
        return pd.DataFrame(columns=expected_cols)
    try:
        df = pd.read_excel(path, engine='openpyxl')
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        df = df[expected_cols]
        df.fillna("", inplace=True)
        return df
    except Exception as e:
        st.warning(f"⚠️ خطأ أثناء قراءة Excel: {e}. سيتم إنشاء DataFrame افتراضي.")
        return pd.DataFrame(columns=expected_cols)

excel_data = safe_load_excel(workbook_path)

# =====================================================
# 🤖 تهيئة المساعد القانوني
# =====================================================
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
    return {
        "العمال": [
            {"العنوان": "احسب مكافأة نهاية الخدمة", "الوصف": "استخدم الحاسبة لتقدير مستحقاتك.", "النوع": "حاسبة", "link": "#", "icon": "🧮", "img": f"{ICON_PATH}service_end.png"},
            {"العنوان": "راجع حقوقك الأساسية", "الوصف": "تعرف على حقوقك وفق القانون الأردني.", "النوع": "توعية", "link": "#", "icon": "📚", "img": f"{ICON_PATH}rights.png"}
        ],
        "اصحاب العمل": [
            {"العنوان": "حاسبة تكاليف الموظفين", "الوصف": "تقدير التزامات الأجور والضرائب.", "النوع": "حاسبة", "link": "#", "icon": "🧮", "img": f"{ICON_PATH}service_end.png"}
        ],
        "مفتشو العمل": [
            {"العنوان": "نموذج تقرير تفتيش", "الوصف": "نماذج جاهزة للتوثيق.", "النوع": "نموذج", "link": "#", "icon": "📄", "img": f"{ICON_PATH}practice.png"}
        ],
        "الباحثون والمتدربون": [
            {"العنوان": "استعراض السوابق القانونية", "الوصف": "اطلع على الحالات السابقة.", "النوع": "بحث", "link": "#", "icon": "🔍", "img": f"{ICON_PATH}legal_case.png"}
        ]
    }

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
# 🏠 الصفحة الرئيسية الحديثة مع بطاقات الفئات
# =====================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

def show_home():
    st.title(f"⚖️ {config.get('APP_NAME')}")
    st.markdown("<h4 style='color:gray;'>اختر فئتك للانتقال إلى القسم المناسب:</h4>", unsafe_allow_html=True)

    categories = [
        {"label": "👷 العمال", "key": "workers", "color":"#3b82f6", "img": f"{ICON_PATH}workers.png"},
        {"label": "🏢 أصحاب العمل", "key": "employers", "color":"#10b981", "img": f"{ICON_PATH}employers.png"},
        {"label": "🕵️ مفتشو العمل", "key": "inspectors", "color":"#f59e0b", "img": f"{ICON_PATH}inspectors.png"},
        {"label": "📖 الباحثون والمتدربون", "key": "researchers", "color":"#6366f1", "img": f"{ICON_PATH}researchers.png"},
        {"label": "⚙️ الإعدادات", "key": "settings", "color":"#9333ea", "img": f"{ICON_PATH}settings.png"}
    ]

    cols = st.columns(len(categories))
    for idx, cat in enumerate(categories):
        with cols[idx]:
            st.markdown(
                f"""
                <div style='
                    background: {cat['color']};
                    padding: 25px;
                    border-radius: 20px;
                    text-align: center;
                    cursor: pointer;
                    transition: transform 0.2s;
                '>
                    <img src='{cat['img']}' width='60px' style='margin-bottom:15px;'/>
                    <h4 style='color:white; margin-bottom:5px;'>{cat['label']}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"اختيار {cat['label']}", key=f"btn_{cat['key']}"):
                st.session_state.current_page = cat["key"]

# الانتقال للصفحة الحالية
pages = {
    "home": show_home,
    "workers": workers_section,
    "employers": employers_section,
    "inspectors": inspectors_section,
    "researchers": researchers_section,
    "settings": settings_page
}

# زر العودة للصفحة الرئيسية
if st.session_state.current_page != "home" and st.button("⬅️ العودة للصفحة الرئيسية"):
    st.session_state.current_page = "home"
else:
    pages[st.session_state.current_page]()

# =====================================================
# 🕒 تذييل رسمي
# =====================================================
st.markdown(
    f"<hr><center><small>{config.get('FOOTER', {}).get('TEXT')}</small></center>",
    unsafe_allow_html=True
)