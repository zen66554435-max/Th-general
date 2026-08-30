# ZeroDay Web Pentest Lab

مختبر تدريبي متوسط مبني بـ Flask.

## التشغيل محليًا

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

افتح `http://127.0.0.1:5000`

حساب التدريب:
- student / student123

## Render

ارفع المشروع إلى GitHub ثم أنشئ Web Service على Render.
يمكن استخدام `render.yaml` أو:
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app`

## ملاحظات أمنية

هذا المشروع مختبر تعليمي متعمد الضعف. لا تستخدمه لتخزين بيانات حقيقية أو كلمات مرور حقيقية.
للتدريب الأفضل تشغيله في بيئة منفصلة، وإزالة الـFlags الظاهرة من `/challenges` قبل التسليم.
