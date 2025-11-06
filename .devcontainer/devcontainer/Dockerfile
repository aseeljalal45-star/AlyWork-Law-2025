# Base image Python 3.11
FROM python:3.11-slim

# إعداد البيئة
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

# تثبيت أدوات أساسية
RUN apt-get update && \
    apt-get install -y git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# نسخ ملفات المشروع
COPY . /workspace

# تحديث pip وتثبيت المتطلبات
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# إعداد متغيرات البيئة الافتراضية
ENV WORKBOOK_PATH="AlyWork_Law_Pro_v2025_v24_ColabStreamlitReady.xlsx"
ENV SHEET_URL="https://docs.google.com/spreadsheets/d/1aCnqHzxWh8RlIgCleHByoCPHMzI1i5fCjrpizcTxGVc/export?format=csv"
ENV THEME="فاتح"
ENV LANG="ar"
ENV CACHE_TTL=600
ENV AI_ENABLE=true
ENV AI_MAX_HISTORY=20
ENV RECOMMENDER_MAX_CARDS=6
ENV DEBUG_MODE=false

# فتح المنفذ الافتراضي لـ Streamlit
EXPOSE 8501

# Command افتراضي لتشغيل Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]