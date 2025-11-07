import streamlit as st

# ⚙️ إعدادات التصميم المتقدمة
config = st.session_state.get("config", {})
ICON_PATH = config.get("UI", {}).get("ICON_PATH", "assets/icons/")

# ==============================
# 🎨 تطبيق التصميم المتميز
# ==============================
def apply_ui_theme():
    """تطبيق تنسيقات UI متقدمة"""
    st.markdown("""
    <style>
    /* تحسينات عامة للواجهة */
    .main .block-container {
        padding-top: 2rem;
    }
    
    /* تحسينات للهواتف */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem;
        }
    }
    
    /* إخفاء عناصر Streamlit الافتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 🗨️ فقاعات المحادثة المحسنة
# ==============================
def message_bubble(sender, text, is_user=False, timestamp=None):
    """
    فقاعة محادثة محسنة مع طابع زمني
    
    Args:
        sender (str): اسم المرسل
        text (str): النص
        is_user (bool): هل هو المستخدم؟
        timestamp (str): الطابع الزمني
    """
    bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" if is_user else "#F8F9FA"
    color = "white" if is_user else "#2D3748"
    align = "right" if is_user else "left"
    border_radius = "18px 18px 4px 18px" if is_user else "18px 18px 18px 4px"
    
    timestamp_html = f"""
    <div style="text-align: {align}; font-size: 0.7rem; color: {'rgba(255,255,255,0.8)' if is_user else '#718096'}; margin-top: 0.3rem;">
        {timestamp if timestamp else ''}
    </div>
    """ if timestamp else ""
    
    st.markdown(
        f"""
        <div style="
            background: {bg}; 
            color: {color}; 
            padding: 12px 16px; 
            border-radius: {border_radius};
            text-align: {align}; 
            margin: 8px 0; 
            max-width: 70%; 
            word-wrap: break-word;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
            transition: all 0.3s ease;
            margin-{'left' if is_user else 'right'}: auto;
            margin-{'right' if is_user else 'left'}: 0;
        ">
            <div style="font-weight: 600; font-size: 0.8rem; margin-bottom: 0.3rem; opacity: 0.9;">
                {sender}
            </div>
            <div style="font-size: 0.95rem; line-height: 1.4;">
                {text}
            </div>
            {timestamp_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# ==============================
# 🏷️ عناوين الأقسام المحسنة
# ==============================
def section_header(title, icon="⚖️", subtitle=None, divider=True):
    """
    عنوان قسم محسن مع خيارات متقدمة
    
    Args:
        title (str): العنوان الرئيسي
        icon (str): الأيقونة
        subtitle (str): العنوان الفرعي
        divider (bool): إظهار خط فاصل
    """
    st.markdown(f"## {icon} {title}")
    
    if subtitle:
        st.markdown(f"""
        <p style='
            color: #718096; 
            font-size: 1rem; 
            margin-top: -0.5rem; 
            margin-bottom: 1.5rem;
            line-height: 1.5;
        '>{subtitle}</p>
        """, unsafe_allow_html=True)
    
    if divider:
        st.markdown("---")

# ==============================
# ℹ️ بطاقة معلومات متميزة
# ==============================
def info_card(title, content, color="#F7FAFC", icon=None, border_color="#E2E8F0", action_button=None):
    """
    بطاقة معلومات محسنة مع خيارات إضافية
    
    Args:
        title (str): عنوان البطاقة
        content (str): المحتوى
        color (str): لون الخلفية
        icon (str): أيقونة
        border_color (str): لون الحدود
        action_button (dict): زر إجراء {text: , action: }
    """
    icon_html = f"<span style='font-size: 1.5rem; margin-right: 0.5rem; vertical-align: middle;'>{icon}</span>" if icon else ""
    
    button_html = ""
    if action_button:
        button_html = f"""
        <div style='margin-top: 1rem;'>
            <button style='
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.3s ease;
            ' onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.4)';" 
            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                {action_button['text']}
            </button>
        </div>
        """
    
    st.markdown(
        f"""
        <div style="
            background: {color}; 
            padding: 1.5rem; 
            border-radius: 12px; 
            margin: 0.5rem 0;
            border-left: 4px solid {border_color};
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
            transition: all 0.3s ease;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 20px rgba(0,0,0,0.1)';" 
        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 10px rgba(0,0,0,0.05)';">
            <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; color: #2D3748;">
                {icon_html}{title}
            </div>
            <div style="color: #4A5568; line-height: 1.6; font-size: 0.95rem;">
                {content}
            </div>
            {button_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# ==============================
# 💠 بطاقة صغيرة متميزة
# ==============================
def mini_card(title, content, icon="ℹ️", color="#EDF2F7", link=None, img=None, badge=None):
    """
    بطاقة صغيرة محسنة مع شارات وخيارات متقدمة
    
    Args:
        title (str): العنوان
        content (str): المحتوى
        icon (str): الأيقونة
        color (str): لون الخلفية
        link (str): الرابط
        img (str): صورة
        badge (str): شارة
    """
    img_html = f"<img src='{ICON_PATH}{img}' width='45px' style='margin-bottom: 0.5rem; border-radius: 8px;'>" if img else f"<div style='font-size: 2rem; margin-bottom: 0.5rem;'>{icon}</div>"
    
    link_html = ""
    if link:
        link_html = f"""
        <a href='{link}' target='_blank' style='
            color: #667eea; 
            text-decoration: none;
            font-weight: 500;
            font-size: 0.8rem;
            display: inline-block;
            margin-top: 0.5rem;
            transition: all 0.3s ease;
        ' onmouseover="this.style.color='#764ba2'; this.style.transform='translateX(2px)';" 
        onmouseout="this.style.color='#667eea'; this.style.transform='translateX(0)';">
            عرض التفاصيل →
        </a>
        """
    
    badge_html = f"<span style='background: #48BB78; color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.7rem; position: absolute; top: 0.5rem; right: 0.5rem;'>{badge}</span>" if badge else ""
    
    st.markdown(
        f"""
        <div style="
            background: {color}; 
            padding: 1.2rem; 
            border-radius: 12px; 
            margin: 0.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
            transition: all 0.3s ease;
            text-align: center;
            position: relative;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 20px rgba(0,0,0,0.12)';" 
        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)';">
            {badge_html}
            {img_html}
            <div style="font-weight: 600; color: #2D3748; margin-bottom: 0.3rem; font-size: 0.95rem;">
                {title}
            </div>
            <div style="color: #718096; font-size: 0.8rem; line-height: 1.4; margin-bottom: 0.5rem;">
                {content}
            </div>
            {link_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# ==============================
# 🎯 مكونات إضافية متقدمة
# ==============================
def feature_highlight(title, description, icon, features=None):
    """تمييز الميزات بشكل أنيق"""
    
    features_html = ""
    if features:
        features_html = "<div style='margin-top: 1rem;'>"
        for feature in features:
            features_html += f"""
            <div style='display: flex; align-items: center; margin: 0.3rem 0;'>
                <span style='color: #48BB78; margin-left: 0.5rem;'>✓</span>
                <span style='font-size: 0.9rem; color: #4A5568;'>{feature}</span>
            </div>
            """
        features_html += "</div>"
    
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%);
            padding: 1.5rem;
            border-radius: 15px;
            border: 1px solid #E2E8F0;
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: flex-start;">
                <div style="font-size: 2rem; margin-left: 1rem; flex-shrink: 0;">{icon}</div>
                <div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: #2D3748; margin-bottom: 0.5rem;">
                        {title}
                    </div>
                    <div style="color: #718096; line-height: 1.5;">
                        {description}
                    </div>
                    {features_html}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# تطبيق التصميم عند الاستيراد
apply_ui_theme()