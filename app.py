import streamlit as st
import os, pandas as pd
from helpers.mini_ai_smart import MiniLegalAI
from helpers.settings_manager import SettingsManager
from helpers.ui_components import message_bubble, section_header, info_card
from recommender import smart_recommender
import plotly.express as px

# =====================================================
# ⚙️ إعدادات عامة
# =====================================================
settings = SettingsManager()
config = st.session_state.get("config", settings.settings)

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
            ai.build_tfidf_matrix()
            return ai
        except Exception as e:
            st.warning(f"⚠️ لم يتم تهيئة المساعد القانوني بالكامل: {e}")
            return None
    return None

ai = init_ai()

def show_ai_assistant(key_prefix=""):
    if not config.get("AI", {}).get("ENABLE", True) or ai is None:
        st.info("🤖 المساعد غير مفعل حالياً.")
        return
    section_header("🤖 المساعد القانوني الذكي", "🤖")
    query = st.text_input("💬 اكتب سؤالك القانوني هنا:", key=f"{key_prefix}_ai_query")
    if query:
        answer, reference, example = ai.advanced_search(query)
        chat_key = f"chat_history_{key_prefix}" if key_prefix else "chat_history"
        st.session_state.setdefault(chat_key, []).append({"user": query, "ai": answer})
        max_history = config.get("AI", {}).get("MAX_HISTORY", 20)
        for chat in st.session_state[chat_key][-max_history:]:
            message_bubble("👤 المستخدم", chat["user"], is_user=True)
            message_bubble("🤖 المساعد", chat["ai"], is_user=False)
        if reference:
            st.markdown(f"**📜 نص القانون:** {reference}")
        if example:
            st.markdown(f"**💡 مثال تطبيقي:** {example}")

# =====================================================
# 👷 الأقسام
# =====================================================
ICON_PATH = config.get("UI", {}).get("ICON_PATH", "assets/icons/")

def workers_section():
    section_header("👷 قسم العمال", "👷")
    show_ai_assistant("workers")
    smart_recommender("العمال")
    
    st.subheader("🧮 حاسبة مكافأة نهاية الخدمة")
    years = st.number_input("عدد سنوات الخدمة:", min_value=0, step=1, key="workers_years")
    last_salary = st.number_input("آخر راتب شهري:", min_value=0.0, step=10.0, format="%.2f", key="workers_salary")
    if st.button("احسب المكافأة", key="workers_calc_bonus"):
        bonus = 0.5 * last_salary * min(years, 5) + last_salary * max(years - 5, 0)
        st.success(f"💰 مكافأة نهاية الخدمة التقديرية: {bonus:,.2f} دينار")
    
    st.subheader("📚 حقوقك الأساسية كعامل")
    rights_list = [
        "✅ الحق في أجر عادل ومنتظم",
        "✅ الحق في إجازة سنوية مدفوعة",
        "✅ الحق في مكافأة نهاية الخدمة",
        "✅ الحق في بيئة عمل آمنة",
        "✅ الحق في ساعات عمل محددة وفترات راحة"
    ]
    for r in rights_list:
        st.markdown(f"- {r}")
    
    st.subheader("📊 توزيع العمال حسب الأقسام")
    if not excel_data.empty and "القسم" in excel_data.columns:
        counts = excel_data['القسم'].value_counts().reset_index()
        counts.columns = ["القسم", "عدد العمال"]
        fig = px.bar(counts, x="القسم", y="عدد العمال", color="القسم", text="عدد العمال")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ بيانات الأقسام غير متوفرة لعرض الرسم البياني.")

def employers_section():
    section_header("🏢 قسم أصحاب العمل", "🏢")
    show_ai_assistant("employers")
    smart_recommender("اصحاب العمل")

def inspectors_section():
    section_header("🕵️ قسم مفتشو العمل", "🕵️")
    show_ai_assistant("inspectors")
    smart_recommender("مفتشو العمل")

def researchers_section():
    section_header("📖 الباحثون والمتدربون", "📖")
    show_ai_assistant("researchers")
    smart_recommender("الباحثون والمتدربون")

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