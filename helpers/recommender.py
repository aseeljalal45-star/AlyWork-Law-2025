import streamlit as st
from helpers.ui_components import section_header

# تحميل الإعدادات العامة من session_state (إذا كانت موجودة)
config = st.session_state.get("config", {})

# المسارات الافتراضية للأيقونات
ICON_PATH = config.get("UI", {}).get("ICON_PATH", "assets/icons/")
MAX_CARDS = config.get("RECOMMENDER", {}).get("MAX_CARDS", 6)

def get_recommendations_data():
    """بيانات التوصيات الأساسية حسب الفئة"""
    data = {
        "العمال": [
            {"العنوان": "احسب مكافأة نهاية الخدمة", "الوصف": "استخدم الحاسبة لتقدير مستحقاتك.", "النوع": "حاسبة", "link": "#", "icon": "🧮", "img": f"{ICON_PATH}service_end.png"},
            {"العنوان": "راجع حقوقك الأساسية", "الوصف": "تعرف على حقوقك وفق القانون الأردني.", "النوع": "توعية", "link": "#", "icon": "📚", "img": f"{ICON_PATH}rights.png"},
            {"العنوان": "اطلع على سوابق قضائية", "الوصف": "أحكام مشابهة لحالتك.", "النوع": "قانوني", "link": "#", "icon": "⚖️", "img": f"{ICON_PATH}legal_case.png"},
            {"العنوان": "تطبيقات عملية", "الوصف": "أمثلة تطبيقية للمواد القانونية.", "النوع": "تعليمي", "link": "#", "icon": "💡", "img": f"{ICON_PATH}practice.png"}
        ],
        "اصحاب العمل": [
            {"العنوان": "حاسبة تكاليف الموظفين", "الوصف": "تقدير التزامات الأجور والضرائب.", "النوع": "حاسبة", "link": "#", "icon": "🧮", "img": f"{ICON_PATH}service_end.png"},
            {"العنوان": "الامتثال القانوني", "الوصف": "راجع التزاماتك وفق القانون الأردني.", "النوع": "امتثال", "link": "#", "icon": "⚖️", "img": f"{ICON_PATH}legal_case.png"}
        ],
        "مفتشو العمل": [
            {"العنوان": "نموذج تقرير تفتيش", "الوصف": "نماذج جاهزة للتوثيق.", "النوع": "نموذج", "link": "#", "icon": "📄", "img": f"{ICON_PATH}practice.png"}
        ],
        "الباحثون والمتدربون": [
            {"العنوان": "استعراض السوابق القانونية", "الوصف": "اطلع على الحالات السابقة.", "النوع": "بحث", "link": "#", "icon": "🔍", "img": f"{ICON_PATH}legal_case.png"}
        ]
    }
    return data

def smart_recommender(role_label="العمال", n=None):
    """عرض التوصيات الذكية في واجهة أنيقة"""
    recommendations = get_recommendations_data().get(role_label, [])
    
    if not recommendations:
        st.info("ℹ️ لا توجد توصيات حالياً لهذه الفئة.")
        return

    section_header("💡 اقتراحات ذكية لك", "💡")

    n = n or MAX_CARDS
    cols = st.columns(3)

    # أنماط الألوان الرسمية للتصنيفات
    type_styles = {
        "حاسبة": "linear-gradient(135deg, #3b82f6, #1d4ed8)",
        "توعية": "linear-gradient(135deg, #10b981, #059669)",
        "قانوني": "linear-gradient(135deg, #6366f1, #4338ca)",
        "تعليمي": "linear-gradient(135deg, #f59e0b, #d97706)",
        "امتثال": "linear-gradient(135deg, #9333ea, #7e22ce)",
        "مالي": "linear-gradient(135deg, #ec4899, #db2777)",
        "مرجع": "linear-gradient(135deg, #14b8a6, #0d9488)",
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