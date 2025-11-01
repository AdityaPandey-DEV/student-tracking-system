# 🚀 Quick Email Test Guide

## ✅ Your Configuration Status: **READY!**

Your `.env` file shows:
- ✅ SendGrid properly configured
- ✅ API key is valid (69 chars, starts with 'SG.')
- ✅ All required settings present

## 🧪 To Actually Test Email Sending:

### On Render (Where it actually matters):

**Method 1: Use Management Command**
1. Go to Render Dashboard → Your Service → **Shell** tab
2. Run:
   ```bash
   python manage.py test_sendgrid_email kingsong7060@gmail.com
   ```

**Method 2: Test via Registration**
1. Visit: https://student-tracking-system-e1hq.onrender.com/register/student/
2. Register with email: `kingsong7060@gmail.com`
3. Check inbox for OTP email

**Method 3: Django Shell**
```python
python manage.py shell
>>> from django.core.mail import send_mail
>>> from django.conf import settings
>>> send_mail('Test', 'Test email', settings.DEFAULT_FROM_EMAIL, ['kingsong7060@gmail.com'])
```

---

### To Test Locally (Optional):

If you want to test locally, you need Django installed:

```bash
# Install dependencies
pip install -r requirements.txt

# Then run
python manage.py test_sendgrid_email kingsong7060@gmail.com
```

**Note**: Local testing uses your `.env` file, but actual production email should be tested on Render where environment variables are set.

