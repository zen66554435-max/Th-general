FROM python:3.11-slim

WORKDIR /app

# تثبيت المتطلبات
COPY requirements_v2.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# نسخ التطبيق
COPY app_v2.py app.py
COPY templates/ templates/
COPY static/ static/

# تعيين البيئة
ENV PORT=5000
ENV DB_PATH=/tmp/lab.db
ENV PYTHONUNBUFFERED=1

# تشغيل
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]
