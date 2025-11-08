import streamlit as st
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# ========================================
# تحميل إعدادات البيئة
# ========================================
load_dotenv()

# ========================================
# 🛠 دوال بديلة لـ ui_components
# ========================================
def section_header(title, subtitle=""):
    st.markdown(f"### {title}\n**{subtitle}**")

def message_bubble(text, sender="system"):
    st.write(f"{sender}: {text}")

def info_card(title, content):
    st.info(f"**{title}**\n{content}")

def mini_card(title, content):
    st.write(f"**{title}**: {content}")

def feature_highlight(title, description):
    st.write(f"**{title}**: {description}")

# ========================================
# استيراد المكونات الأخرى
# ========================================
from helpers.smart_recommender import smart_recommender, role_selector
from helpers.mini_ai_smart import MiniLegalAI
from helpers.settings_manager import SettingsManager
from helpers.data_loader import DataLoader

# ========================================
# إعداد التطبيق والبيئة
# ========================================
def setup_application():
    env_config = {
        "APP_INFO": {
            "APP_NAME": os.getenv("APP_NAME", "⚖️ منصة قانون العمل الذكية"),
            "VERSION": os.getenv("APP_VERSION", "v25.1"),
            "SUPPORT_EMAIL": os.getenv("SUPPORT_EMAIL", "support@alyworklaw.com")
        },
        "DATA_SOURCES": {
            "WORKBOOK_PATH": os.getenv("WORKBOOK_PATH", "data/AlyWork_Law_Pro_v2025_v24_ColabStreamlitReady.xlsx"),
            "SHEET_URL": os.getenv("SHEET_URL", "")
        },
        "AI_FEATURES": {
            "ENABLE_AI": os.getenv("AI_ENABLE", "true").lower() == "true",
            "MAX_HISTORY": int(os.getenv("AI_MAX_HISTORY", "20"))
        }
    }
    settings_manager = SettingsManager()
    settings_manager.update(env_config)
    return settings_manager

settings_manager = setup_application()
config = st.session_state.get("config", settings_manager.settings)

# ========================================
# إعداد صفحة Streamlit
# ========================================
st.set_page_config(
    page_title=config.get("APP_INFO", {}).get("APP_NAME", "منصة قانون العمل الذكية"),
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# تحميل CSS مخصص
# ========================================
def load_custom_css():
    css_file = "assets/styles_official.css"
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .main-header { background: linear-gradient(135deg, #1E3A8A, #2563EB); color: white; padding: 2rem; border-radius: 20px; text-align: center; margin-bottom: 2rem; }
        .feature-card { background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 1rem 0; transition: transform 0.3s ease; }
        .feature-card:hover { transform: translateY(-5px); }
        </style>
        """, unsafe_allow_html=True)

load_custom_css()

# ========================================
# تهيئة المكونات الذكية
# ========================================
@st.cache_resource
def init_ai_assistant():
    workbook_path = config.get("DATA_SOURCES", {}).get("WORKBOOK_PATH", "")
    return MiniLegalAI(workbook_path)

@st.cache_resource
def init_data_loader():
    return DataLoader()

ai_assistant = init_ai_assistant()
data_loader = init_data_loader()

# ========================================
# 🏠 الصفحة الرئيسية
# ========================================
def show_home_page():
    st.markdown(f"""
    <div class="main-header">
        <h1 style="margin:0; font-size: 3rem;">{config.get("APP_INFO", {}).get("APP_NAME", "⚖️ منصة قانون العمل الذكية")}</h1>
        <p style="font-size: 1.2rem; margin: 1rem 0 0 0; opacity: 0.9;">
        المنصة الشاملة لحماية حقوق العمال وتقديم الاستشارات القانونية الذكية
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📊 المواد القانونية", "150+")
    with col2: st.metric("👥 المستفيدين", "5,000+")
    with col3: st.metric("⚖️ المحافظات", "12")
    with col4: st.metric("💼 نسبة الرضا", "95%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### 🎯 التوصيات الذكية لك")
    selected_role = role_selector()
    smart_recommender(selected_role, show_header=False)
    
    st.markdown("### 🚀 خدماتنا الرئيسية")
    features = [
        {"icon": "🧮", "title": "الحاسبات القانونية", "description": "حساب دقيق للمستحقات المالية وفق القانون الأردني", "features": ["مكافأة نهاية الخدمة", "بدل العمل الإضافي", "الإجازات المرضية"]},
        {"icon": "📝", "title": "محاكي الشكوى الذكي", "description": "تحليل الانتهاكات وتقديم الإجراءات القانونية المناسبة", "features": ["تحليل آلي", "توصيات مخصصة", "نماذج جاهزة"]},
        {"icon": "🏛️", "title": "الجهات المختصة", "description": "دليل شامل للجهات الرسمية في جميع المحافظات", "features": ["عنوان دقيق", "معلومات اتصال", "أوقات العمل"]},
    ]
    
    cols = st.columns(3)
    for idx, feature in enumerate(features):
        with cols[idx]:
            st.markdown(f"""
            <div class="feature-card">
                <div style="font-size: 3rem; text-align: center; margin-bottom: 1rem;">{feature['icon']}</div>
                <h3 style="text-align: center;">{feature['title']}</h3>
                <p style="text-align: center; color: #666;">{feature['description']}</p>
                <div style="text-align: center;">
                    {" • ".join([f"<span style='background: #E3F2FD; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.8rem; margin: 0.1rem; display: inline-block;'>{f}</span>" for f in feature['features']])}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ========================================
# 🧭 نظام التنقل الرئيسي
# ========================================
def main():
    with st.sidebar:
        st.markdown(f"<div style='text-align: center; padding: 1rem;'><h2>⚖️ {config.get('APP_INFO', {}).get('APP_NAME', 'منصة قانون العمل')}</h2><p style='color: #666; font-size: 0.9rem;'>الإصدار {config.get('APP_INFO', {}).get('VERSION', 'v25.1')}</p></div>", unsafe_allow_html=True)
        st.markdown("---")
        page_options = {
            "🏠 الصفحة الرئيسية": show_home_page,
            # يمكنك إضافة باقي الأقسام هنا بنفس الطريقة
        }
        selected_page = st.selectbox("اختر القسم", list(page_options.keys()))
        st.markdown("---")
        st.markdown("### 📞 الدعم الفني")
        st.write("📧 support@alyworklaw.com")
        st.write("📞 06-5802666")
        st.write("🕒 الأحد - الخميس: 8:00 ص - 3:00 م")
    
    if selected_page in page_options: page_options[selected_page]()
    
    st.markdown("---")
    footer_text = config.get("FOOTER", {}).get("TEXT", "© 2025 منصة قانون العمل الذكية — جميع الحقوق محفوظة.")
    st.markdown(f"<center><small>{footer_text}</small></center>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()