import streamlit as st

config = st.session_state.get("config", {})
ICON_PATH = config.get("UI", {}).get("ICON_PATH", "assets/icons/")

def message_bubble(sender, text, is_user=False):
    bg = "#007BFF" if is_user else "#F1F1F1"
    color = "white" if is_user else "black"
    align = "right" if is_user else "left"
    border_radius = "15px 5px 15px 15px" if is_user else "5px 15px 15px 15px"
    st.markdown(
        f"""<div style="background:{bg}; color:{color}; padding:12px 16px; border-radius:{border_radius};
             text-align:{align}; margin:6px 0; max-width:80%; word-wrap: break-word;
             box-shadow: 2px 2px 8px rgba(0,0,0,0.1); transition: all 0.2s;">{text}</div>""",
        unsafe_allow_html=True
    )

def section_header(title, icon="⚖️", subtitle=None):
    st.markdown(f"## {icon} {title}")
    if subtitle:
        st.markdown(f"<p style='color:gray;'>{subtitle}</p>", unsafe_allow_html=True)

def info_card(title, content, color="#F9FAFB", icon=None):
    icon_html = f"<span style='font-size:20px; margin-right:5px;'>{icon}</span>" if icon else ""
    st.markdown(
        f"""<div style="background:{color}; padding:12px; border-radius:12px; margin:6px 0;
             box-shadow:0 3px 6px rgba(0,0,0,0.1); transition: transform 0.2s, box-shadow 0.2s;">
             <b>{icon_html}{title}</b><br><p style='margin:5px 0; font-size:14px;'>{content}</p></div>""",
        unsafe_allow_html=True
    )

def mini_card(title, content, icon="ℹ️", color="#E0F7FA", link=None):
    link_html = f"<a href='{link}' target='_blank' style='color:#007BFF; text-decoration:underline;'>عرض التفاصيل</a>" if link else ""
    st.markdown(
        f"""<div style="background:{color}; padding:10px; border-radius:10px; margin:5px 0;
             box-shadow:0 2px 5px rgba(0,0,0,0.1); transition: transform 0.2s;">
             <b>{icon} {title}</b><br><span style='font-size:13px;'>{content}</span><br>{link_html}</div>""",
        unsafe_allow_html=True
    )