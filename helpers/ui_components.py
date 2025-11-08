import streamlit as st

def section_header(title, subtitle=None):
    """عرض عنوان قسم مع وصف"""
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"<p style='color: #666;'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("---")

def message_bubble(text, is_user=False):
    """فقاعة محادثة"""
    bg_color = "#007BFF" if is_user else "#F1F1F1"
    text_color = "white" if is_user : "black"
    align = "right" if is_user else "left"
    
    st.markdown(f"""
    <div style="
        background: {bg_color};
        color: {text_color};
        padding: 12px 16px;
        border-radius: 15px;
        margin: 8px 0;
        text-align: {align};
        max-width: 80%;
        margin-{'left' if is_user else 'right'}: auto;
    ">{text}</div>
    """, unsafe_allow_html=True)

def info_card(title, content, icon="ℹ️"):
    """بطاقة معلومات"""
    st.markdown(f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #2563EB;
    ">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 1.5rem; margin-left: 0.5rem;">{icon}</span>
            <h4 style="margin: 0;">{title}</h4>
        </div>
        <p style="margin: 0.5rem 0 0 0; color: #666;">{content}</p>
    </div>
    """, unsafe_allow_html=True)