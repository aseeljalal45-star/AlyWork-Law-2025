import streamlit as st
from helpers.ui_components import section_header

# ==============================
# ⚙️ إعدادات عامة من config
# ==============================
config = st.session_state.get("config", {})
ICON_PATH = config.get("UI", {}).get("ICON_PATH", "assets/icons/")
MAX_CARDS = config.get("RECOMMENDER", {}).get("MAX_CARDS", 6)

# ==============================
# 💡 بيانات التوصيات حسب الفئة
# ==============================
def get_recommendations_data():
    data = {
        "العمال": [
            {"العنوان": "احسب مكافأة نهاية الخدمة", "الوصف": "استخدم الحاسبة لتقدير مستحقاتك.", "النوع": "حاسبة", "link": "#", "icon": "🧮", "img": f"{ICON_PATH}service_end.png"},
            {"العنوان": "راجع حقوقك الأساسية", "الوصف": "تعرف على حقوقك وفق القانون الأردني.", "النوع": "توعية", "link": "#", "icon": "📚", "img": f"{ICON_PATH}rights.png"},
            {"العنوان": "اطلع على سوابق قضائية", "الوصف": "أحكام مشابهة لحالتك.", "النوع": "قانوني", "link": "#", "icon": "⚖️", "img": f"{ICON_PATH}legal_case.png"},
            {"العنوان": "تطبيقات عملية", "الوصف": "أمثلة تطبيقية للمواد القانونية.", "النوع": "تعليمي", "link": "#", "icon": "💡", "img": f"{ICON_PATH}practice.png"}
        ],
        "اصحاب العمل": [
            {"العنوان": "إدارة الموظفين بكفاءة", "الوصف": "أفضل الممارسات لإدارة العمل.", "النوع": "توعية", "link": "#", "icon": "🏢", "img": f"{ICON_PATH}management.png"},
            {"العنوان": "تقييم الالتزام بالقانون", "الوصف": "راجع امتثال منشأتك للقانون.", "النوع": "امتثال", "link": "#", "icon": "✔️", "img": f"{ICON_PATH}compliance.png"}
        ],
        "مفتشو العمل": [
            {"العنوان": "دليل التفتيش", "الوصف": "خطوات التفتيش على المنشآت.", "النوع": "مرجع", "link": "#", "icon": "🕵️", "img": f"{ICON_PATH}inspection.png"}
        ],
        "الباحثون والمتدربون": [
            {"العنوان": "مواد قانونية للتعلم", "الوصف": "اطلع على نصوص قانونية مختارة.", "النوع": "تعليمي", "link": "#", "icon": "📖", "img": f"{ICON_PATH}study.png"}
        ]
    }
    return data

# ==============================
# 💡 دالة عرض التوصيات الذكية
# ==============================
def smart_recommender(role_label="العمال", n=None):
    recommendations = get_recommendations_data().get(role_label, [])
    
    # fallback إذا لم توجد توصيات
    if not recommendations:
        st.warning("⚠️ لا توجد توصيات حالياً لهذه الفئة.")
        return
    
    section_header("💡 اقتراحات ذكية لك", "💡")
    n = n or MAX_CARDS
    cols = st.columns(3)
    
    # ألوان حسب نوع التوصية
    type_styles = {
        "حاسبة": "linear-gradient(135deg, #FFD700, #FFA500)",
        "توعية": "linear-gradient(135deg, #00BFFF, #1E90FF)",
        "قانوني": "linear-gradient(135deg, #FF4500, #FF6347)",
        "تعليمي": "linear-gradient(135deg, #32CD32, #7CFC00)",
        "امتثال": "linear-gradient(135deg, #8A2BE2, #9400D3)",
        "مالي": "linear-gradient(135deg, #FF69B4, #FF1493)",
        "مرجع": "linear-gradient(135deg, #20B2AA, #3CB371)",
        "نموذج": "linear-gradient(135deg, #FFA500, #FF8C00)",
        "بحث": "linear-gradient(135deg, #7FFF00, #32CD32)"
    }
    
    for idx, rec in enumerate(recommendations[:n]):
        with cols[idx % len(cols)]:
            style = type_styles.get(rec['النوع'], "#D3D3D3")
            st.markdown(
                f"""<div style="background: {style}; border-radius:15px; padding:15px; margin:5px;
                     box-shadow: 2px 4px 15px rgba(0,0,0,0.2); transition: transform 0.3s, box-shadow 0.3s; text-align:center;">
                     <img src='{rec['img']}' alt='icon' width='50px' style='margin-bottom:10px;'/>
                     <h4>{rec['icon']} {rec['العنوان']}</h4>
                     <p style='font-size:14px; margin:5px 0;'>{rec['الوصف']}</p>
                     <a href='{rec['link']}' target='_blank' style='color:#fff; text-decoration:underline;'>اضغط هنا للتفاصيل</a>
                     </div>""",
                unsafe_allow_html=True
            )