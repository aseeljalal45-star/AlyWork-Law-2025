import streamlit as st
import os
import pandas as pd
from helpers.mini_ai_smart import MiniLegalAI
from helpers.settings_manager import SettingsManager
from helpers.ui_components import section_header
from datetime import datetime

# =====================================================
# ⚙️ الإعدادات العامة
# =====================================================
settings = SettingsManager()
config = st.session_state.get("config", settings.settings)

st.set_page_config(
    page_title=config.get("APP_NAME", "منصة قانون العمل الأردني الذكية"),
    page_icon="⚖️",
    layout="wide"
)

# =====================================================
# 🎨 تحميل CSS الرسمي
# =====================================================
def load_official_css(css_file="assets/styles_official.css"):
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_official_css()

# =====================================================
# 📊 تحميل البيانات
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
        return pd.DataFrame(columns=expected_cols)
    try:
        df = pd.read_excel(path, engine='openpyxl')
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        df.fillna("", inplace=True)
        return df
    except Exception as e:
        st.warning(f"⚠️ خطأ أثناء قراءة Excel: {e}")
        return pd.DataFrame(columns=expected_cols)

data = load_google_sheets(SHEET_URL)
excel_data = load_excel(WORKBOOK_PATH)

# =====================================================
# 🤖 تهيئة المساعد القانوني
# =====================================================
def init_ai():
    try:
        ai = MiniLegalAI(WORKBOOK_PATH)
        ai.db = excel_data
        ai.build_tfidf_matrix()
        return ai
    except Exception as e:
        st.warning(f"⚠️ لم يتم تهيئة المساعد القانوني بالكامل: {e}")
        return None

if "ai_instance" not in st.session_state:
    st.session_state["ai_instance"] = init_ai()
ai = st.session_state["ai_instance"]

# =====================================================
# 🧮 الحاسبات القانونية
# =====================================================
def calculators_tab():
    section_header("🧮 الحاسبات القانونية", "🧮")
    
    calcs = [
        {"title": "مكافأة نهاية الخدمة", "desc": "حساب مكافأة نهاية الخدمة حسب سنوات العمل والأجر."},
        {"title": "بدلات العمل الإضافي والليلي والعطلات", "desc": "حساب مستحقات العمل الإضافي."},
        {"title": "التعويض عن الإجازات غير المستغلة", "desc": "حساب التعويض عن الإجازات السنوية."},
        {"title": "بدل النقل والسكن", "desc": "حساب بدلات النقل والسكن الشهرية."},
        {"title": "حساب الأجور الشهرية مع الخصومات", "desc": "حساب الراتب بعد الخصومات والاستقطاعات."},
        {"title": "استحقاقات الفصل التعسفي", "desc": "تقدير التعويض عند الفصل التعسفي."},
        {"title": "إجازة الحمل والولادة", "desc": "حساب مستحقات إجازة الأمومة."},
        {"title": "مكافأة الإجازات المرضية", "desc": "حساب التعويض عن الإجازات المرضية."},
        {"title": "استحقاقات تغيير الوظيفة أو النقل الداخلي", "desc": "حساب التعويضات عند النقل أو تغيير الوظيفة."},
        {"title": "حاسبة الدوام الجزئي", "desc": "حساب الأجر للدوام الجزئي."},
        {"title": "تعويض إصابات العمل", "desc": "حساب التعويضات المترتبة على إصابات العمل."}
    ]
    
    cols = st.columns(3)
    for i, calc in enumerate(calcs):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#E8F6F3; padding:25px; border-radius:20px; margin-bottom:20px; text-align:center; box-shadow:0 3px 6px rgba(0,0,0,0.1);">
                <h4 style="color:#117A65;">{calc['title']}</h4>
                <p style="color:#1C2833;">{calc['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# 📚 حقوق العمال والتزاماتهم
# =====================================================
def rights_tab():
    section_header("📚 حقوق العمال والتزاماتهم", "📚")
    
    categories = [
        {"title": "⚖️ حقوق العمال", "items": ["الأجر والمكافآت","الإجازات السنوية والمرضية","ظروف العمل وسلامته","الحماية من الفصل التعسفي"]},
        {"title": "👩‍🍼 حقوق المرأة العاملة", "items": ["إجازة الحمل والولادة","حق الرضاعة","عدم الفصل أثناء الحمل","بيئة عمل آمنة ومناسبة"]},
        {"title": "📋 التزامات العامل", "items": ["الالتزام بساعات العمل","أداء المهام بدقة","المحافظة على أسرار المنشأة","إشعار صاحب العمل عند الغياب"]},
        {"title": "🏢 التزامات صاحب العمل", "items": ["دفع الأجور في موعدها","توفير بيئة عمل آمنة","منح الإجازات القانونية","تسجيل العامل في الضمان الاجتماعي"]}
    ]
    
    cols = st.columns(2)
    for idx, cat in enumerate(categories):
        with cols[idx % 2]:
            st.markdown(f"""
            <div style="background:#D6EAF8; padding:20px; border-radius:20px; margin-bottom:20px; box-shadow:0 3px 6px rgba(0,0,0,0.1);">
                <h4 style="color:#154360;">{cat['title']}</h4>
                <ul style="color:#1B2631;">{''.join([f"<li>{item}</li>" for item in cat['items']])}</ul>
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# 📝 محاكي الشكوى الذكي
# =====================================================
def complaint_simulator_tab():
    section_header("📝 محاكي الشكوى", "📝")
    st.info("🧩 هذه الأداة تساعدك على معرفة انتهاكات حقوقك والتوصية بالإجراءات المناسبة.")
    
    # بيانات العامل
    st.subheader("📌 بيانات العامل")
    الاسم = st.text_input("اسم العامل (اختياري)")
    سنوات_العمل = st.number_input("عدد سنوات العمل:", min_value=0, step=1)
    الراتب = st.number_input("الراتب الشهري (بالدينار الأردني):", min_value=0)
    
    # نوع الانتهاك
    st.subheader("⚠️ نوع الانتهاك")
    نوع_الانتهاك = st.selectbox("اختر نوع الانتهاك:", [
        "عدم دفع الأجر/المستحقات",
        "فصل تعسفي",
        "العمل الإضافي غير المدفوع",
        "عدم منح الإجازات القانونية",
        "ظروف عمل خطرة أو غير آمنة",
        "انتهاكات أخرى"
    ])
    
    # تفاصيل إضافية
    st.subheader("📝 تفاصيل إضافية")
    وصف_الحالة = st.text_area("صف باختصار ما حدث:", "")

    if st.button("🔍 تحليل الحالة"):
        st.info("⏳ جاري تحليل الانتهاك وتحديد الإجراءات الموصى بها...")
        توصية = ""
        if نوع_الانتهاك == "عدم دفع الأجر/المستحقات":
            توصية = "📌 تقديم شكوى لدى مديرية العمل لمطالبة بدفع المستحقات."
        elif نوع_الانتهاك == "فصل تعسفي":
            توصية = "📌 تقديم شكوى فصل تعسفي ومطالبة التعويض وفق القانون."
        elif نوع_الانتهاك == "العمل الإضافي غير المدفوع":
            توصية = "📌 توثيق ساعات العمل الإضافية ومطالبة الدفع."
        elif نوع_الانتهاك == "عدم منح الإجازات القانونية":
            توصية = "📌 تقديم شكوى لدى مديرية العمل للحصول على الإجازات."
        elif نوع_الانتهاك == "ظروف عمل خطرة أو غير آمنة":
            توصية = "📌 رفع شكوى لدى الجهات التفتيشية للحصول على بيئة عمل آمنة."
        else:
            توصية = "📌 تقديم شكوى مفصلة لدى مديرية العمل لبحث الحالة."

        st.subheader("📄 التقرير القانوني")
        st.markdown(f"""
        <div style="background:#FDFEFE; padding:20px; border-radius:20px; box-shadow:0 3px 6px rgba(0,0,0,0.1);">
        - <b>العامل:</b> {الاسم or "غير محدد"}<br>
        - <b>سنوات العمل:</b> {سنوات_العمل}<br>
        - <b>الراتب:</b> {الراتب} دينار<br>
        - <b>نوع الانتهاك:</b> {نوع_الانتهاك}<br>
        - <b>وصف الحالة:</b> {وصف_الحالة or 'لا يوجد وصف'}<br>
        - <b>التوصية:</b> {توصية}
        </div>
        """, unsafe_allow_html=True)
        st.success("✅ التحليل تم بنجاح")

# =====================================================
# 🏛️ الجهات المختصة حسب المحافظات
# =====================================================
def complaints_places_tab():
    section_header("🏛️ أماكن تقديم الشكاوى والجهات المختصة", "🏛️")
    محافظة = st.selectbox("اختر المحافظة:", [
        "عمان", "إربد", "الزرقاء", "البلقاء", "الكرك", "معان",
        "الطفيلة", "المفرق", "مادبا", "جرش", "عجلون", "العقبة"
    ])
    الجهات = {
        "عمان": {"الجهة":"مديرية العمل – عمان","العنوان":"عمان، شارع عيسى الناوري 11","الهاتف":"06‑5802666","البريد":"info@mol.gov.jo","الموقع":"http://www.mol.gov.jo"},
        "إربد": {"الجهة":"مديرية العمل – إربد","العنوان":"إربد، الأردن","الهاتف":"06‑xxxxxxx","البريد":"irbid@mol.gov.jo","الموقع":"http://www.mol.gov.jo/irbid"},
    }
    info = الجهات.get(محافظة)
    if info:
        st.markdown(f"""
        <div style="background:#E8F8F5;padding:15px;border-radius:15px;margin-bottom:10px; box-shadow:0 3px 6px rgba(0,0,0,0.1);">
        <b>{info['الجهة']}</b><br>
        العنوان: {info['العنوان']}<br>
        الهاتف: {info['الهاتف']}<br>
        البريد: {info['البريد']}<br>
        الموقع: <a href="{info['الموقع']}" target="_blank">{info['الموقع']}</a>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ لا توجد بيانات متوفّرة لهذه المحافظة بعد.")

# =====================================================
# 👷 صفحة العمال
# =====================================================
def workers_section():
    selected_tab = st.session_state.get("workers_tab", None)
    
    if selected_tab is None:
        # عرض الأقسام فقط
        st.markdown("### 👷 أقسام صفحة العمال")
        tabs = [
            {"label": "🧮", "name": "🧮 الحاسبات"},
            {"label": "📚", "name": "📚 حقوق العمال"},
            {"label": "📝", "name": "📝 محاكي الشكوى"},
            {"label": "🏛️", "name": "🏛️ الجهات المختصة"},
        ]
        TAB_BG = "#F0F8FF"
        TAB_HOVER_BG = "#D6EAF8"
        TAB_TEXT_COLOR = "#1C2833"
        TAB_ICON_SIZE = "50px"
        cols = st.columns(len(tabs))
        for i, tab in enumerate(tabs):
            with cols[i]:
                if st.button(f'<div style="background:{TAB_BG}; border-radius:25px; padding:30px 20px; text-align:center; font-weight:600; color:{TAB_TEXT_COLOR}; font-size:18px; box-shadow:0 4px 8px rgba(0,0,0,0.1); cursor:pointer;">{tab["label"]}<br>{tab["name"]}</div>', key=tab["name"], use_container_width=True):
                    st.session_state["workers_tab"] = tab["name"]
    else:
        # عرض الصفحة الفرعية المختارة
        if selected_tab == "🧮 الحاسبات":
            calculators_tab()
        elif selected_tab == "📚 حقوق العمال":
            rights_tab()
        elif selected_tab == "📝 محاكي الشكوى":
            complaint_simulator_tab()
        elif selected_tab == "🏛️ الجهات المختصة":
            complaints_places_tab()
        if st.button("⬅️ العودة للأقسام"):
            st.session_state["workers_tab"] = None

# =====================================================
# 🏠 الصفحة الرئيسية
# =====================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

def show_home():
    CARD_GRADIENT = "linear-gradient(135deg, #89CFF0, #B0E0E6)"
    CARD_TEXT_COLOR = "#000000"
    
    st.markdown(f"""
    <div style="text-align:center; padding:25px; background: {CARD_GRADIENT};
                border-radius:20px; color:{CARD_TEXT_COLOR}; margin-bottom:30px;">
        <h1 style="margin-bottom:10px;">⚖️ {config.get('APP_NAME')}</h1>
        <p style="font-size:18px; margin:0;">
        منصة ذكية للوصول إلى حقوق العمال، الحاسبات القانونية، محاكي الشكاوى، والجهات المختصة
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("👷 اذهب إلى صفحة العمال"):
        st.session_state.current_page = "workers"

# =====================================================
# 🧭 نظام التنقل
# =====================================================
pages = {
    "home": show_home,
    "workers": workers_section,
}
pages[st.session_state.current_page]()

# =====================================================
# ⚖️ Footer
# =====================================================
st.markdown(f"<hr><center><small>{config.get('FOOTER', {}).get('TEXT')}</small></center>", unsafe_allow_html=True)