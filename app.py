import streamlit as st
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# =====================================================
# 🎨 إعدادات التصميم المتقدمة
# =====================================================
st.set_page_config(
    page_title="⚖️ منصة قانون العمل الذكية",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تطبيق التصميم المتميز
def apply_premium_design():
    st.markdown("""
    <style>
    /* التصميم الرئيسي */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* الهيدر الرئيسي */
    .main-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        padding: 3rem 2rem;
        border-radius: 0 0 30px 30px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* بطاقات الخدمات */
    .service-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid #e0e6ef;
        height: 100%;
        text-align: center;
    }
    
    .service-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .service-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* الأزرار */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 15px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* علامات التبويب المخصصة */
    .custom-tab {
        background: #f8f9fa;
        padding: 1rem 2rem;
        border-radius: 15px;
        margin: 0.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .custom-tab:hover {
        background: #e9ecef;
        border-color: #667eea;
    }
    
    .custom-tab.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* الإحصائيات */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #667eea;
    }
    
    /* محاكي الشكوى */
    .complaint-form {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* نتائج التحليل */
    .analysis-result {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

apply_premium_design()

# =====================================================
# 🏠 الصفحة الرئيسية المتميزة
# =====================================================
def show_premium_home():
    # الهيدر الرئيسي
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; font-size: 3rem;">⚖️ منصة قانون العمل الذكية</h1>
        <p style="font-size: 1.2rem; margin: 1rem 0 0 0; opacity: 0.9;">
        المنصة الشاملة لحماية حقوق العمال وتقديم الاستشارات القانونية الذكية
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # إحصائيات سريعة
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3>📊 150+</h3>
            <p>مادة قانونية</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3>👥 5,000+</h3>
            <p>مستفيد شهرياً</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-card">
            <h3>⚖️ 12</h3>
            <p>محافظة مغطاة</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="stat-card">
            <h3>💼 95%</h3>
            <p>نسبة الرضا</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # الخدمات الرئيسية
    st.markdown("### 🎯 خدماتنا الرئيسية")
    
    services = [
        {
            "icon": "🧮",
            "title": "الحاسبات القانونية",
            "desc": "حساب المستحقات المالية بدقة وفق القانون الأردني",
            "features": ["مكافأة نهاية الخدمة", "بدل العمل الإضافي", "الإجازات المرضية"]
        },
        {
            "icon": "📝",
            "title": "محاكي الشكوى الذكي",
            "desc": "تحليل الانتهاكات وتقديم الإجراءات القانونية المناسبة",
            "features": ["تحليل آلي", "توصيات مخصصة", "نماذج جاهزة"]
        },
        {
            "icon": "🏛️",
            "title": "الجهات المختصة",
            "desc": "دليل شامل للجهات الرسمية في جميع المحافظات",
            "features": ["عنوان دقيق", "معلومات اتصال", "أوقات العمل"]
        },
        {
            "icon": "📚",
            "title": "المرجع القانوني",
            "desc": "مكتبة شاملة للقوانين واللوائح والتشريعات",
            "features": ["بحث متقدم", "أمثلة عملية", "تحديثات مستمرة"]
        },
        {
            "icon": "💼",
            "title": "استشارات قانونية",
            "desc": "إجابات فورية على استفساراتك القانونية",
            "features": ["ردود فورية", "مراجع قانونية", "حالات مشابهة"]
        },
        {
            "icon": "📊",
            "title": "تحليل البيانات",
            "desc": "إحصائيات وتقارير عن قضايا العمل",
            "features": ["تقارير شهرية", "تحليل الاتجاهات", "رؤى قانونية"]
        }
    ]
    
    # عرض الخدمات في شبكة 2x3
    cols = st.columns(3)
    for idx, service in enumerate(services):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="service-card">
                <div class="service-icon">{service['icon']}</div>
                <h3>{service['title']}</h3>
                <p>{service['desc']}</p>
                <div style="text-align: left; margin-top: 1rem;">
                    {''.join([f'<div style="margin: 0.3rem 0;">✅ {feature}</div>' for feature in service['features']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # كيفية العمل
    st.markdown("### 🔄 كيف تعمل المنصة؟")
    
    steps = [
        {"icon": "1️⃣", "title": "اختر الخدمة", "desc": "اختر من بين خدماتنا المتعددة"},
        {"icon": "2️⃣", "title": "أدخل البيانات", "desc": "املأ النموذج المخصص لاحتياجاتك"},
        {"icon": "3️⃣", "title": "احصل على النتائج", "desc": "تلقى التحليل والتوصيات الفورية"}
    ]
    
    step_cols = st.columns(3)
    for idx, step in enumerate(steps):
        with step_cols[idx]:
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">{step['icon']}</div>
                <h4>{step['title']}</h4>
                <p style="color: #666;">{step['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# 🧮 الحاسبات القانونية المحسنة
# =====================================================
def show_enhanced_calculators():
    st.markdown("""
    <div class="main-header" style="border-radius: 20px; margin-bottom: 2rem;">
        <h2>🧮 الحاسبات القانونية</h2>
        <p>حساب دقيق للمستحقات المالية وفق القانون الأردني</p>
    </div>
    """, unsafe_allow_html=True)
    
    # اختيار نوع الآلة الحاسبة
    calc_type = st.selectbox(
        "اختر نوع الحاسبة:",
        [
            "مكافأة نهاية الخدمة",
            "بدلات العمل الإضافي",
            "التعويض عن الإجازات",
            "بدل النقل والسكن",
            "استحقاقات الفصل التعسفي",
            "إجازة الحمل والولادة"
        ]
    )
    
    st.markdown("""
    <div class="complaint-form">
    """, unsafe_allow_html=True)
    
    if calc_type == "مكافأة نهاية الخدمة":
        st.subheader("🧮 حاسبة مكافأة نهاية الخدمة")
        
        col1, col2 = st.columns(2)
        with col1:
            years = st.number_input("عدد سنوات الخدمة", min_value=0, max_value=50, value=5)
            basic_salary = st.number_input("الأجر الأساسي (دينار)", min_value=0, value=500)
        
        with col2:
            service_type = st.selectbox("نهاية الخدمة", ["استقالة", "إنهاء خدمة", "بلوغ سن المعاش"])
            last_salary = st.number_input("آخر راتب (دينار)", min_value=0, value=500)
        
        if st.button("🔄 حساب المكافأة", use_container_width=True):
            # محاكاة حساب المكافأة (يمكن استبدالها بالحسابات الفعلية)
            if service_type == "استقالة":
                if years <= 5:
                    compensation = (years * 0.5 * basic_salary)
                else:
                    compensation = (5 * 0.5 * basic_salary) + ((years - 5) * basic_salary)
            else:
                compensation = years * basic_salary
            
            st.markdown(f"""
            <div class="analysis-result">
                <h3>📊 نتائج الحساب</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div>عدد سنوات الخدمة: <strong>{years}</strong></div>
                    <div>نهاية الخدمة: <strong>{service_type}</strong></div>
                    <div>الأجر الأساسي: <strong>{basic_salary} دينار</strong></div>
                    <div>المكافأة المستحقة: <strong>{compensation:,.0f} دينار</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    elif calc_type == "بدلات العمل الإضافي":
        st.subheader("⏰ حاسبة العمل الإضافي")
        
        col1, col2 = st.columns(2)
        with col1:
            hourly_rate = st.number_input("الأجر الساعي (دينار)", min_value=0.0, value=2.5)
            overtime_hours = st.number_input("ساعات العمل الإضافي", min_value=0, value=10)
        
        with col2:
            overtime_type = st.selectbox("نوع العمل الإضافي", ["نهاري", "ليلي", "عطلة رسمية"])
            normal_hours = st.number_input("ساعات العمل العادية", min_value=0, value=8)
        
        if st.button("🔄 حساب البدل", use_container_width=True):
            # محاكاة حساب البدل
            if overtime_type == "نهاري":
                rate = 1.25
            elif overtime_type == "ليلي":
                rate = 1.5
            else:
                rate = 2.0
            
            overtime_pay = overtime_hours * hourly_rate * rate
            
            st.markdown(f"""
            <div class="analysis-result">
                <h3>💰 نتائج الحساب</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div>ساعات العمل الإضافي: <strong>{overtime_hours}</strong></div>
                    <div>نوع العمل الإضافي: <strong>{overtime_type}</strong></div>
                    <div>الأجر الساعي: <strong>{hourly_rate} دينار</strong></div>
                    <div>البدل المستحق: <strong>{overtime_pay:,.2f} دينار</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# 📝 محاكي الشكوى الذكي المحسن
# =====================================================
def show_enhanced_complaint_simulator():
    st.markdown("""
    <div class="main-header" style="border-radius: 20px; margin-bottom: 2rem;">
        <h2>📝 محاكي الشكوى الذكي</h2>
        <p>تحليل الانتهاكات وتقديم الحلول القانونية المثلى</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="complaint-form">
    """, unsafe_allow_html=True)
    
    # معلومات العامل
    st.subheader("👤 معلومات العامل")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("الاسم الكامل")
        years_of_service = st.slider("سنوات الخدمة", 0, 40, 3)
    
    with col2:
        phone = st.text_input("رقم الهاتف")
        monthly_salary = st.number_input("الراتب الشهري (دينار)", min_value=0, value=500)
    
    # نوع الانتهاك
    st.subheader("⚠️ تفاصيل الانتهاك")
    violation_type = st.selectbox(
        "نوع الانتهاك",
        [
            "عدم دفع الأجر/المستحقات",
            "الفصل التعسفي",
            "العمل الإضافي غير المدفوع", 
            "عدم منح الإجازات القانونية",
            "ظروف عمل غير آمنة",
            "تمييز أو تحرش",
            "عدم التسجيل في الضمان",
            "انتهاكات أخرى"
        ]
    )
    
    # تفاصيل إضافية
    violation_details = st.text_area(
        "وصف تفصيلي للانتهاك",
        placeholder="صف ما حدث بالتفصيل، including التواريخ والأماكن والأشخاص المتورطين..."
    )
    
    # المستندات (محاكاة)
    st.subheader("📎 المستندات المرفقة")
    doc_col1, doc_col2, doc_col3 = st.columns(3)
    with doc_col1:
        st.checkbox("عقد العمل")
    with doc_col2:
        st.checkbox("كشوف المرتبات")
    with doc_col3:
        st.checkbox("مستندات أخرى")
    
    if st.button("🔍 تحليل الحالة وتقديم التوصيات", use_container_width=True):
        with st.spinner("🔄 جاري تحليل الحالة وتوليد التوصيات..."):
            # محاكاة التحليل الذكي
            import time
            time.sleep(2)
            
            # نتائج التحليل
            st.markdown("""
            <div class="analysis-result">
                <h3>📋 تقرير التحليل القانوني</h3>
            """, unsafe_allow_html=True)
            
            # التوصيات حسب نوع الانتهاك
            recommendations = {
                "عدم دفع الأجر/المستحقات": [
                    "تقديم شكوى لمديرية العمل المختصة",
                    "طلب صورة من كشوف المرتبات",
                    "توثيق جميع عمليات الدفع",
                    "الاحتفاظ بجميع المراسلات"
                ],
                "الفصل التعسفي": [
                    "طلب تعويض الفصل التعسفي",
                    "تقديم شكوى لمحكمة العمل",
                    "إثبات عدم وجود مبرر للفصل",
                    "الاحتفاظ بجميع الوثائق"
                ],
                "العمل الإضافي غير المدفوع": [
                    "توثيق ساعات العمل الإضافي",
                    "تقديم طلب بدفع المستحقات",
                    "الاحتفاظ بسجلات الحضور",
                    "طلب تعويض عن الساعات الإضافية"
                ]
            }
            
            recs = recommendations.get(violation_type, [
                "تقديم شكوى مفصلة لمديرية العمل",
                "الاحتفاظ بجميع الأدلة والوثائق",
                "استشارة محامٍ متخصص"
            ])
            
            st.markdown("""
                <div style="margin: 1.5rem 0;">
                    <h4>✅ الإجراءات الموصى بها:</h4>
            """, unsafe_allow_html=True)
            
            for i, rec in enumerate(recs, 1):
                st.markdown(f"<div style='margin: 0.5rem 0;'>{i}. {rec}</div>", unsafe_allow_html=True)
            
            # الجهات المختصة
            st.markdown("""
                <h4 style='margin-top: 2rem;'>🏛️ الجهات المختصة:</h4>
                <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;'>
                    <strong>مديرية العمل - عمان</strong><br>
                    📍 عمان، شارع عيسى الناوري 11<br>
                    📞 06-5802666<br>
                    📧 info@mol.gov.jo
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# 🏛️ الجهات المختصة المحسنة
# =====================================================
def show_enhanced_authorities():
    st.markdown("""
    <div class="main-header" style="border-radius: 20px; margin-bottom: 2rem;">
        <h2>🏛️ الجهات المختصة</h2>
        <p>دليل شامل للجهات الرسمية في جميع محافظات المملكة</p>
    </div>
    """, unsafe_allow_html=True)
    
    # خريطة المحافظات
    governorates = [
        "عمان", "إربد", "الزرقاء", "البلقاء", "الكرك", "معان",
        "الطفيلة", "المفرق", "مادبا", "جرش", "عجلون", "العقبة"
    ]
    
    selected_gov = st.selectbox("اختر المحافظة", governorates)
    
    # بيانات الجهات (موسعة)
    authorities_data = {
        "عمان": {
            "مديرية العمل - عمان": {
                "address": "عمان، شارع عيسى الناوري 11",
                "phone": "06-5802666",
                "email": "info@mol.gov.jo",
                "website": "http://www.mol.gov.jo",
                "hours": "الأحد - الخميس: 8:00 ص - 3:00 م",
                "services": ["تسجيل شكاوى", "استشارات قانونية", "تفتيش العمل"]
            },
            "محكمة العمل - عمان": {
                "address": "عمان، منطقة عبدون",
                "phone": "06-5802000",
                "email": "court@mol.gov.jo",
                "hours": "الأحد - الخميس: 8:00 ص - 2:00 م"
            }
        },
        "إربد": {
            "مديرية العمل - إربد": {
                "address": "إربد، المنطقة الشمالية",
                "phone": "02-7241000",
                "email": "irbid@mol.gov.jo",
                "hours": "الأحد - الخميس: 8:00 ص - 3:00 م",
                "services": ["تسجيل شكاوى", "تفتيش العمل", "تسجيل عقود"]
            }
        }
    }
    
    gov_data = authorities_data.get(selected_gov, authorities_data["عمان"])
    
    for authority, info in gov_data.items():
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
            <h3 style="color: #2c3e50; margin-bottom: 1rem;">{authority}</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <strong>📍 العنوان:</strong><br>{info['address']}
                </div>
                <div>
                    <strong>📞 الهاتف:</strong><br>{info['phone']}
                </div>
                <div>
                    <strong>🕒 أوقات العمل:</strong><br>{info['hours']}
                </div>
                <div>
                    <strong>📧 البريد الإلكتروني:</strong><br>{info['email']}
                </div>
            </div>
            {f"<div style='margin-top: 1rem;'><strong>✅ الخدمات:</strong><br>" + " • ".join(info.get('services', [])) + "</div>" if info.get('services') else ""}
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# 📱 نظام التنقل الجانبي المتميز
# =====================================================
def create_premium_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚖️</div>
            <h2>منصة قانون العمل</h2>
            <p style="color: #666; font-size: 0.9rem;">المنصة الذكية لحماية حقوق العمال</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # قائمة التنقل
        menu_options = [
            {"icon": "🏠", "label": "الصفحة الرئيسية"},
            {"icon": "🧮", "label": "الحاسبات القانونية"},
            {"icon": "📝", "label": "محاكي الشكوى"},
            {"icon": "🏛️", "label": "الجهات المختصة"},
            {"icon": "📚", "label": "المرجع القانوني"},
            {"icon": "💼", "label": "الاستشارات"},
            {"icon": "📊", "label": "التقارير والإحصائيات"}
        ]
        
        for option in menu_options:
            if st.button(f"{option['icon']} {option['label']}", use_container_width=True, key=option['label']):
                st.session_state.current_page = option['label']
        
        st.markdown("---")
        
        # معلومات الاتصال
        st.markdown("""
        <div style="text-align: center; color: #666;">
            <p><strong>📞 الدعم الفني:</strong> 06-5802666</p>
            <p><strong>📧 البريد الإلكتروني:</strong> info@mol.gov.jo</p>
            <p><strong>🕒 أوقات العمل:</strong><br>الأحد - الخميس<br>8:00 ص - 3:00 م</p>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# 🧭 نظام إدارة الحالة
# =====================================================
if 'current_page' not in st.session_state:
    st.session_state.current_page = "الصفحة الرئيسية"

# إنشاء الشريط الجانبي
create_premium_sidebar()

# توجيه الصفحات
if st.session_state.current_page == "الصفحة الرئيسية":
    show_premium_home()
elif st.session_state.current_page == "الحاسبات القانونية":
    show_enhanced_calculators()
elif st.session_state.current_page == "محاكي الشكوى":
    show_enhanced_complaint_simulator()
elif st.session_state.current_page == "الجهات المختصة":
    show_enhanced_authorities()
else:
    show_premium_home()

# =====================================================
# 🦶 الفوتر المتميز
# =====================================================
st.markdown("""
<div style="background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); color: white; padding: 2rem; border-radius: 20px; margin-top: 3rem; text-align: center;">
    <h3>⚖️ منصة قانون العمل الذكية</h3>
    <p>المنصة الرائدة في تقديم الخدمات القانونية للعمال في المملكة الأردنية</p>
    <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem; flex-wrap: wrap;">
        <div>📞 06-5802666</div>
        <div>📧 info@mol.gov.jo</div>
        <div>📍 عمان، الأردن</div>
    </div>
    <p style="margin-top: 1rem; opacity: 0.8;">© 2024 منصة قانون العمل الذكية - جميع الحقوق محفوظة</p>
</div>
""", unsafe_allow_html=True)