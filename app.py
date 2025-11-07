import streamlit as st
import os
import pandas as pd
import plotly.express as px
from helpers.settings_manager import SettingsManager
from helpers.ui_components import section_header, info_card

# =====================================================
# ⚙️ الإعدادات العامة
# =====================================================
settings = SettingsManager()
config = st.session_state.get("config", settings.settings)

st.set_page_config(
    page_title=config.get("APP_NAME", "منصة العمال الذكية"),
    page_icon="👷",
    layout="wide"
)

# =====================================================
# 🎨 تحميل CSS احترافي
# =====================================================
def load_css(css_file="assets/styles_official.css"):
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# =====================================================
# 📊 تحميل البيانات وحفظها
# =====================================================
WORKBOOK_PATH = settings.get("WORKBOOK_PATH", config.get("WORKBOOK_PATH"))

def load_excel(path, expected_cols=None):
    expected_cols = expected_cols or ["الفئة","الحاسبة","النتيجة","تفاصيل"]
    if not os.path.exists(path):
        return pd.DataFrame(columns=expected_cols)
    try:
        df = pd.read_excel(path, engine="openpyxl")
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        df.fillna("", inplace=True)
        return df
    except:
        return pd.DataFrame(columns=expected_cols)

data_excel = load_excel(WORKBOOK_PATH)

def save_excel(df):
    df.to_excel(WORKBOOK_PATH, index=False, engine="openpyxl")

# =====================================================
# 🧮 الحاسبات القانونية حسب الفئات
# =====================================================
def wages_calculators():
    st.subheader("💰 الأجور والمكافآت")
    salary = st.number_input("الراتب الأساسي (بالدينار الأردني)", min_value=0.0)
    overtime_hours = st.number_input("ساعات العمل الإضافية", min_value=0)
    overtime_rate = st.number_input("سعر الساعة الإضافية", min_value=0.0)
    allowances = st.number_input("بدلات (نقل، سكن، غذاء)", min_value=0.0)
    deductions = st.number_input("الخصومات", min_value=0.0)

    if st.button("حساب الراتب الشهري الإجمالي"):
        total = salary + (overtime_hours*overtime_rate) + allowances - deductions
        st.success(f"💵 الراتب الشهري الإجمالي: {total} د.أ")
        # حفظ
        new_row = {"الفئة":"الأجور والمكافآت", "الحاسبة":"الراتب الشهري", "النتيجة":total, "تفاصيل":f"الراتب {salary}، ساعات إضافية {overtime_hours}"}
        global data_excel
        data_excel = pd.concat([data_excel, pd.DataFrame([new_row])], ignore_index=True)
        save_excel(data_excel)

def leaves_calculators():
    st.subheader("🌴 الإجازات والاستحقاقات")
    years_worked = st.number_input("عدد سنوات الخدمة", min_value=0)
    annual_leave_days = st.number_input("أيام الإجازة السنوية المستحقة", min_value=0)
    sick_leave_days = st.number_input("أيام الإجازة المرضية", min_value=0)
    maternity_leave_days = st.number_input("أيام إجازة الحمل والولادة", min_value=0)

    if st.button("حساب إجمالي الإجازات"):
        total = annual_leave_days + sick_leave_days + maternity_leave_days
        st.success(f"📅 إجمالي الإجازات المستحقة: {total} يوم")
        new_row = {"الفئة":"الإجازات والاستحقاقات", "الحاسبة":"إجمالي الإجازات", "النتيجة":total, "تفاصيل":f"سنوات الخدمة {years_worked}"}
        global data_excel
        data_excel = pd.concat([data_excel, pd.DataFrame([new_row])], ignore_index=True)
        save_excel(data_excel)

def end_of_service_calculators():
    st.subheader("🏆 مكافأة نهاية الخدمة والتعويضات")
    salary = st.number_input("الراتب الأساسي للحساب", min_value=0.0, key="eos_salary")
    years_worked = st.number_input("عدد سنوات الخدمة", min_value=0, key="eos_years")
    if st.button("حساب مكافأة نهاية الخدمة"):
        severance = salary * years_worked
        st.success(f"💰 مكافأة نهاية الخدمة: {severance} د.أ")
        new_row = {"الفئة":"مكافأة نهاية الخدمة", "الحاسبة":"مكافأة نهاية الخدمة", "النتيجة":severance, "تفاصيل":f"راتب {salary}، سنوات {years_worked}"}
        global data_excel
        data_excel = pd.concat([data_excel, pd.DataFrame([new_row])], ignore_index=True)
        save_excel(data_excel)

def special_cases_calculators():
    st.subheader("⚡ الدوام الجزئي وتغييرات الوظيفة")
    hours_worked = st.number_input("عدد ساعات الدوام الجزئي", min_value=0)
    rate_per_hour = st.number_input("الأجر لكل ساعة", min_value=0.0)
    if st.button("حساب أجر الدوام الجزئي"):
        total = hours_worked * rate_per_hour
        st.success(f"💵 أجر الدوام الجزئي: {total} د.أ")
        new_row = {"الفئة":"الدوام الجزئي", "الحاسبة":"الدوام الجزئي", "النتيجة":total, "تفاصيل":f"ساعات {hours_worked}, أجر {rate_per_hour}"}
        global data_excel
        data_excel = pd.concat([data_excel, pd.DataFrame([new_row])], ignore_index=True)
        save_excel(data_excel)

def calculators_tab():
    st.title("🧮 الحاسبات القانونية")
    categories = ["الأجور والمكافآت", "الإجازات والاستحقاقات", "مكافأة نهاية الخدمة", "الدوام الجزئي"]
    choice = st.radio("اختر الفئة:", categories, horizontal=True)
    if choice == "الأجور والمكافآت":
        wages_calculators()
    elif choice == "الإجازات والاستحقاقات":
        leaves_calculators()
    elif choice == "مكافأة نهاية الخدمة":
        end_of_service_calculators()
    elif choice == "الدوام الجزئي":
        special_cases_calculators()

# =====================================================
# 📚 حقوق العمال والتزاماتهم
# =====================================================
def rights_tab():
    section_header("📚 حقوق العمال والتزاماتهم", "📚")
    st.markdown("""
    <style>
    .card {background: linear-gradient(135deg,#FFD700,#D4AF37); padding:20px; border-radius:20px; margin-bottom:15px;}
    .card-title {font-size:20px; font-weight:bold; margin-bottom:10px;}
    </style>
    """, unsafe_allow_html=True)
    info_card("⚖️ حقوق العامل", ["مكافأة نهاية الخدمة", "الأجر الشهري وبدل العمل الإضافي", "بدل النقل والسكن", "الإجازات السنوية والمرضية"])
    info_card("👩‍🍼 حقوق المرأة العاملة", ["إجازة الحمل والولادة", "الحق في الرضاعة", "عدم الفصل أثناء الحمل"])
    info_card("📋 التزامات العامل", ["الالتزام بساعات الدوام", "المحافظة على أسرار المنشأة", "إشعار صاحب العمل عند الغياب"])
    info_card("🏢 التزامات صاحب العمل", ["دفع الأجور في موعدها", "توفير بيئة عمل آمنة", "منح الإجازات القانونية", "تسجيل العامل في الضمان الاجتماعي"])

# =====================================================
# 📝 محاكي الشكوى
# =====================================================
def complaint_simulator_tab():
    section_header("📝 محاكي الشكوى", "📝")
    st.info("🧩 هذه الأداة تتيح لك محاكاة تقديم شكوى عمالية إلكترونيًا (قيد التطوير).")

# =====================================================
# 🏛️ أماكن تقديم الشكاوى والجهات المختصة
# =====================================================
def complaints_places_tab():
    section_header("🏛️ أماكن تقديم الشكاوى والجهات المختصة", "🏛️")
    entities = [
        {"الجهة":"وزارة العمل","العنوان":"عمان، الأردن","الهاتف":"06-1234567","البريد":"info@mol.gov.jo","الموقع":"http://www.mol.gov.jo"},
        {"الجهة":"التفتيش العمالي","العنوان":"عمان، الأردن","الهاتف":"06-7654321","البريد":"inspection@mol.gov.jo","الموقع":"http://www.mol.gov.jo/inspection"}
    ]
    for e in entities:
        st.markdown(f"""
        <div style="background:#f0f0f0;padding:15px;border-radius:15px;margin-bottom:10px;">
        <b>{e['الجهة']}</b><br>
        العنوان: {e['العنوان']}<br>
        الهاتف: {e['الهاتف']}<br>
        البريد: {e['البريد']}<br>
        الموقع: <a href="{e['الموقع']}" target="_blank">{e['الموقع']}</a>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# 👷 صفحة العمال الرئيسية
# =====================================================
def workers_section():
    tabs = ["🧮 الحاسبات", "📚 حقوق العمال", "📝 محاكي الشكوى", "🏛️ الجهات المختصة"]
    selected_tab = st.radio("اختر التبويب:", tabs, horizontal=True)
    if selected_tab == "🧮 الحاسبات":
        calculators_tab()
    elif selected_tab == "📚 حقوق العمال":
        rights_tab()
    elif selected_tab == "📝 محاكي الشكوى":
        complaint_simulator_tab()
    elif selected_tab == "🏛️ الجهات المختصة":
        complaints_places_tab()

# =====================================================
# 🏠 الصفحة الرئيسية
# =====================================================
def show_home():
    st.markdown(f"<h1 style='text-align:center'>👷 {config.get('APP_NAME')}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>أداة ذكية لحساب الحقوق العمالية في الأردن</p>", unsafe_allow_html=True)
    if st.button("➡️ اذهب إلى قسم العمال"):
        st.session_state.current_page = "workers"

# =====================================================
# 🧭 نظام التنقل
# =====================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

pages = {
    "home": show_home,
    "workers": workers_section,
}

pages[st.session_state.current_page]()

# =====================================================
# ⚖️ Footer
# =====================================================
st.markdown(f"<hr><center><small>{config.get('FOOTER', {}).get('TEXT','© جميع الحقوق محفوظة')}</small></center>", unsafe_allow_html=True)