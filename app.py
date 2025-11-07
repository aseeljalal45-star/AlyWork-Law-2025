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
def load_official_css(css_file="assets/styles_official.css"):
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.info(f"ℹ️ ملف CSS الرسمي غير موجود: {css_file}")

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

data = load_google_sheets(SHEET_URL)
excel_data = load_excel(WORKBOOK_PATH)

# =====================================================
# 🤖 تهيئة المساعد القانوني
# =====================================================
def init_ai():
    if os.path.exists(WORKBOOK_PATH):
        try:
            ai = MiniLegalAI(WORKBOOK_PATH)
            ai.db = excel_data
            ai.build_tfidf_matrix()
            return ai
        except Exception as e:
            st.warning(f"⚠️ لم يتم تهيئة المساعد القانوني بالكامل: {e}")
            return None
    return None

ai = init_ai()

def show_ai_assistant():
    if not config.get("AI", {}).get("ENABLE", True) or ai is None:
        st.info("🤖 المساعد غير مفعل حالياً.")
        return
    section_header("🤖 المساعد القانوني الذكي", "🤖")
    query = st.text_input("💬 اكتب سؤالك القانوني هنا:")
    if query:
        answer, reference, example = ai.advanced_search(query)
        st.session_state.setdefault("chat_history", []).append({"user": query, "ai": answer})
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

# التدرج الذهبي للبطاقات والنص
CARD_GRADIENT = "linear-gradient(135deg, #FFD700, #D4AF37)"
CARD_TEXT_COLOR = "#000000"

def get_recommendations(role):
    mapping = {
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
    return mapping.get(role, [])

def smart_recommender(role="العمال", n=None):
    recs = get_recommendations(role)
    if not recs:
        st.info("ℹ️ لا توجد توصيات حالياً لهذه الفئة.")
        return
    section_header("💡 اقتراحات ذكية لك", "💡")
    n = n or MAX_CARDS
    cols = st.columns(3)
    for idx, rec in enumerate(recs[:n]):
        with cols[idx % len(cols)]:
            st.markdown(
                f"""
                <div style="background: {CARD_GRADIENT};
                            border-radius:20px;
                            padding:20px;
                            margin:10px;
                            box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
                            text-align:center;
                            color:{CARD_TEXT_COLOR};
                            transition: transform 0.3s;
                            cursor:pointer;"
                            onmouseover="this.style.transform='scale(1.05)';"
                            onmouseout="this.style.transform='scale(1)';">
                    <img src='{rec['img']}' alt='icon' width='60px' style='margin-bottom:12px;'/>
                    <h3 style='margin-bottom:6px;'>{rec['icon']} {rec['العنوان']}</h3>
                    <p style='font-size:15px; opacity:0.9;'>{rec['الوصف']}</p>
                    <a href='{rec['link']}' target='_blank' style='color:{CARD_TEXT_COLOR}; text-decoration:underline;'>اضغط هنا للتفاصيل</a>
                </div>
                """,
                unsafe_allow_html=True
            )

# =====================================================
# 🏠 صفحات الفئات
# =====================================================
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
    section_header("📖 الباحثون والمتدربون", "📖")
    show_ai_assistant()
    smart_recommender("الباحثون والمتدربون")

def settings_page():
    section_header("⚙️ الإعدادات", "⚙️")
    st.write("يمكنك تعديل الإعدادات من هنا.")
    new_path = st.text_input("📁 مسار ملف Excel:", value=WORKBOOK_PATH)
    new_sheet = st.text_input("🗂️ رابط Google Sheet:", value=SHEET_URL)
    if st.button("💾 حفظ"):
        settings.settings["WORKBOOK_PATH"] = new_path
        settings.settings["SHEET_URL"] = new_sheet
        settings.save_settings()
        st.success("✅ تم حفظ الإعدادات بنجاح!")

# =====================================================
# 🏠 الصفحة الرئيسية جديدة احترافية
# =====================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

def show_home():
    st.markdown(f"""
        <div style="text-align:center; padding:20px; background: {CARD_GRADIENT};
                    border-radius:15px; color:{CARD_TEXT_COLOR}; margin-bottom:20px;">
            <h1 style="margin:0; font-size:40px;">⚖️ {config.get('APP_NAME')}</h1>
            <p style="font-size:18px; margin-top:5px;">الوصول السريع إلى أقسام المنصة الذكية</p>
        </div>
    """, unsafe_allow_html=True)

    categories = [
        {"label": "👷 العمال", "key": "workers", "icon": "workers.png"},
        {"label": "🏢 أصحاب العمل", "key": "employers", "icon": "employers.png"},
        {"label": "🕵️ مفتشو العمل", "key": "inspectors", "icon": "inspectors.png"},
        {"label": "📖 الباحثون والمتدربون", "key": "researchers", "icon": "researchers.png"},
        {"label": "⚙️ الإعدادات", "key": "settings", "icon": "settings.png"}
    ]

    cols = st.columns(3)
    for idx, cat in enumerate(categories):
        with cols[idx % 3]:
            st.markdown(f"""
                <div style="background: {CARD_GRADIENT};
                            padding: 25px; border-radius: 25px;
                            text-align: center; cursor: pointer;
                            transition: transform 0.3s, box-shadow 0.3s;
                            box-shadow: 0px 10px 25px rgba(0,0,0,0.15);
                            margin-bottom:20px;">
                    <img src='{ICON_PATH}{cat['icon']}' width='70px' style='margin-bottom:15px;'/>
                    <h3 style='color:{CARD_TEXT_COLOR}; margin-bottom:5px;'>{cat['label']}</h3>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"اختيار {cat['label']}", key=f"btn_{cat['key']}"):
                st.session_state.current_page = cat["key"]

# =====================================================
# 🏠 قاموس الصفحات
# =====================================================
pages = {
    "home": show_home,
    "workers": workers_section,
    "employers": employers_section,
    "inspectors": inspectors_section,
    "researchers": researchers_section,
    "settings": settings_page
}

# =====================================================
# 🔄 الانتقال بين الصفحات
# =====================================================
if st.session_state.current_page != "home" and st.button("⬅️ العودة للصفحة الرئيسية"):
    st.session_state.current_page = "home"
else:
    pages[st.session_state.current_page]()

# =====================================================
# 🕒 Footer
# =====================================================
st.markdown(f"<hr><center><small>{config.get('FOOTER', {}).get('TEXT')}</small></center>", unsafe_allow_html=True)