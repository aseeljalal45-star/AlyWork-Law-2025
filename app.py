import streamlit as st
import os, pandas as pd
from helpers.mini_ai_smart import MiniLegalAI
from helpers.settings_manager import SettingsManager
from helpers.ui_components import message_bubble, section_header, info_card

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
# 🌈 تحميل CSS عالمي متقدم
# =====================================================
def load_advanced_css(css_file="assets/styles_official.css"):
    css = """
    /* عام */
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    h1, h2, h3, h4 { font-weight: 700; }

    /* البطاقات الرئيسية */
    .card-hover {
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        background: linear-gradient(135deg, #4da6ff, #66cc99);
        margin-bottom: 25px;
    }
    .card-hover:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }

    /* النصوص */
    .card-title { font-size: 22px; font-weight: 700; margin-bottom: 10px; }
    .card-desc { font-size: 16px; opacity: 0.85; }

    /* أزرار العودة */
    .back-btn {
        background: #3333ff;
        color: white;
        border-radius: 12px;
        padding: 8px 15px;
        font-weight: 600;
        margin-top: 20px;
    }
    """
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            css += f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_advanced_css()

# =====================================================
# 🏠 الصفحة الرئيسية عالمية
# =====================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

ICON_PATH = config.get("UI", {}).get("ICON_PATH", "assets/icons/")

def show_home():
    # خلفية متدرجة للصفحة
    st.markdown("""
        <div style="padding:50px; border-radius:20px; background: linear-gradient(120deg,#1e3c72,#2a5298);
                    color:white; text-align:center; margin-bottom:30px;">
            <h1 style="font-size:48px; font-weight:800;">⚖️ {}</h1>
            <p style="font-size:20px; opacity:0.9;">منصة ذكية للوصول السريع إلى أقسام قانون العمل الأردني</p>
        </div>
    """.format(config.get('APP_NAME')), unsafe_allow_html=True)

    # الأقسام
    categories = [
        {"label": "👷 العمال", "key": "workers", "color":"#4da6ff", "icon": "workers.png"},
        {"label": "🏢 أصحاب العمل", "key": "employers", "color":"#66cc99", "icon": "employers.png"},
        {"label": "🕵️ مفتشو العمل", "key": "inspectors", "color":"#40c0c0", "icon": "inspectors.png"},
        {"label": "📖 الباحثون والمتدربون", "key": "researchers", "color":"#7f7fff", "icon": "researchers.png"},
        {"label": "⚙️ الإعدادات", "key": "settings", "color":"#b19cd9", "icon": "settings.png"}
    ]

    cols = st.columns(3)
    for idx, cat in enumerate(categories):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="card-hover" style="background: linear-gradient(135deg, {cat['color']}, #2222cc);">
                    <img src="{ICON_PATH}{cat['icon']}" width="80px" style="margin-bottom:15px;"/>
                    <div class="card-title">{cat['label']}</div>
                    <div class="card-desc">اضغط للدخول إلى القسم الخاص بك واستكشاف الميزات.</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"اختيار {cat['label']}", key=f"btn_{cat['key']}"):
                st.session_state.current_page = cat["key"]

# =====================================================
# 🏠 قاموس الصفحات
# =====================================================
def workers_section(): section_header("👷 قسم العمال", "👷"); show_ai_assistant()
def employers_section(): section_header("🏢 قسم أصحاب العمل", "🏢"); show_ai_assistant()
def inspectors_section(): section_header("🕵️ قسم المفتشين", "🕵️"); show_ai_assistant()
def researchers_section(): section_header("📖 الباحثون والمتدربون", "📖"); show_ai_assistant()
def settings_page():
    section_header("⚙️ الإعدادات", "⚙️")
    st.write("يمكنك تعديل الإعدادات من هنا.")
    new_path = st.text_input("📁 مسار ملف Excel:", value=settings.settings.get("WORKBOOK_PATH"))
    new_sheet = st.text_input("🗂️ رابط Google Sheet:", value=settings.settings.get("SHEET_URL"))
    if st.button("💾 حفظ"):
        settings.settings["WORKBOOK_PATH"] = new_path
        settings.settings["SHEET_URL"] = new_sheet
        settings.save_settings()
        st.success("✅ تم حفظ الإعدادات بنجاح!")

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
# 🕒 Footer عالمي
# =====================================================
st.markdown(f"<hr><center><small>{config.get('FOOTER', {}).get('TEXT')}</small></center>", unsafe_allow_html=True)