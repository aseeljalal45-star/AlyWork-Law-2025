# التدرج الذهبي للبطاقات والنصوص والتوهج الداخلي
CARD_GRADIENT = "linear-gradient(135deg, #FFD700, #D4AF37)"
CARD_TEXT_COLOR = "#000000"

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
                            transition: transform 0.3s, box-shadow 0.5s, text-shadow 0.5s;
                            cursor:pointer;"
                            onmouseover="this.style.transform='scale(1.05)'; 
                                         this.style.boxShadow='0px 0px 25px 5px rgba(255,215,0,0.8)';
                                         this.style.textShadow='0 0 8px rgba(255,215,0,0.9)';"
                            onmouseout="this.style.transform='scale(1)'; 
                                        this.style.boxShadow='0px 8px 20px rgba(0,0,0,0.15)';
                                        this.style.textShadow='none';">
                    <img src='{rec['img']}' alt='icon' width='60px' style='margin-bottom:12px;'/>
                    <h3 style='margin-bottom:6px;'>{rec['icon']} {rec['العنوان']}</h3>
                    <p style='font-size:15px; opacity:0.9;'>{rec['الوصف']}</p>
                    <a href='{rec['link']}' target='_blank' style='color:{CARD_TEXT_COLOR}; text-decoration:underline;'>اضغط هنا للتفاصيل</a>
                </div>
                """,
                unsafe_allow_html=True
            )

def show_home():
    st.markdown(f"""
        <div style="text-align:center; padding:20px; background: {CARD_GRADIENT};
                    border-radius:15px; color:{CARD_TEXT_COLOR}; margin-bottom:20px;
                    transition: transform 0.3s, box-shadow 0.5s, text-shadow 0.5s;"
                    onmouseover="this.style.transform='scale(1.02)'; 
                                 this.style.boxShadow='0px 0px 35px 10px rgba(255,215,0,0.9)';
                                 this.style.textShadow='0 0 12px rgba(255,215,0,0.95)';"
                    onmouseout="this.style.transform='scale(1)'; 
                                this.style.boxShadow='0px 10px 25px rgba(0,0,0,0.15)';
                                this.style.textShadow='none';">
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
                            transition: transform 0.3s, box-shadow 0.5s, text-shadow 0.5s;
                            box-shadow: 0px 10px 25px rgba(0,0,0,0.15);
                            margin-bottom:20px;"
                            onmouseover="this.style.transform='scale(1.05)';
                                         this.style.boxShadow='0px 0px 30px 8px rgba(255,215,0,0.8)';
                                         this.style.textShadow='0 0 10px rgba(255,215,0,0.9)';"
                            onmouseout="this.style.transform='scale(1)';
                                        this.style.boxShadow='0px 10px 25px rgba(0,0,0,0.15)';
                                        this.style.textShadow='none';">
                    <img src='{ICON_PATH}{cat['icon']}' width='70px' style='margin-bottom:15px;'/>
                    <h3 style='color:{CARD_TEXT_COLOR}; margin-bottom:5px;'>{cat['label']}</h3>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"اختيار {cat['label']}", key=f"btn_{cat['key']}"):
                st.session_state.current_page = cat["key"]