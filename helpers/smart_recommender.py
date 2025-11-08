import streamlit as st

def get_recommendations_data():
    """إرجاع بيانات التوصيات الذكية المنظمة حسب الفئات"""
    return {
        "👷 العمال": [
            {
                "title": "احسب مكافأة نهاية الخدمة",
                "description": "حساب دقيق لمستحقات نهاية الخدمة وفق القانون الأردني",
                "type": "حاسبة",
                "icon": "🧮",
                "action": "احسب الآن"
            },
            {
                "title": "محاكي الشكوى الذكي", 
                "description": "حلل حالتك واحصل على توصيات قانونية مخصصة",
                "type": "تحليل",
                "icon": "📝",
                "action": "ابدأ التحليل"
            }
        ],
        "🏢 أصحاب العمل": [
            {
                "title": "حاسبة التكاليف الشهرية",
                "description": "تقدير التزامات الأجور والضرائب والاشتراكات",
                "type": "حاسبة", 
                "icon": "💰",
                "action": "احسب التكاليف"
            }
        ]
    }

def smart_recommender(role_label="👷 العمال", n=6, show_header=True):
    """عرض التوصيات الذكية بشكل أنيق"""
    recommendations = get_recommendations_data().get(role_label, [])
    
    if not recommendations:
        st.info("🎯 لا توجد توصيات متاحة حالياً لهذه الفئة")
        return
        
    if show_header:
        st.markdown(f"### 💡 توصيات مخصصة لـ {role_label}")
    
    cols = st.columns(2)
    for idx, rec in enumerate(recommendations[:n]):
        with cols[idx % 2]:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1E3A8A, #2563EB);
                color: white;
                padding: 1.5rem;
                border-radius: 15px;
                margin: 0.5rem 0;
                text-align: center;
            ">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{rec['icon']}</div>
                <h4 style="margin: 0.5rem 0;">{rec['title']}</h4>
                <p style="font-size: 0.9rem; opacity: 0.9;">{rec['description']}</p>
                <button style="
                    background: rgba(255,255,255,0.2);
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 8px;
                    margin-top: 0.5rem;
                ">{rec['action']}</button>
            </div>
            """, unsafe_allow_html=True)

def role_selector():
    """محدد دور المستخدم"""
    roles = ["👷 العمال", "🏢 أصحاب العمل", "🕵️ مفتشو العمل", "📖 الباحثون"]
    return st.selectbox("اختر فئتك", roles, key="role_selector")