# 🔍 Troubleshoot Email Not Arriving

## ❓ Problem: No email received at kingsong7060@gmail.com

Let's systematically check why emails aren't arriving.

## Step 1: Verify SendGrid Configuration on Render

### Check Render Environment Variables

1. Go to **Render Dashboard** → Your Service → **Environment** tab
2. Verify these variables are set:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_PROVIDER=sendgrid
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
SENDGRID_API_KEY=SG.your-actual-api-key-here
DEFAULT_FROM_EMAIL=adityapandey.dev.in@gmail.com
EMAIL_TIMEOUT=10
```

### Important Checks:
- ✅ **SENDGRID_API_KEY**: Must start with `SG.` and be the full key
- ✅ **EMAIL_HOST_USER**: Must be exactly `apikey` (literal string)
- ✅ **DEFAULT_FROM_EMAIL**: Must be your verified sender email

## Step 2: Verify Sender Email in SendGrid

**CRITICAL**: The sender email MUST be verified in SendGrid!

1. Go to: https://app.sendgrid.com/settings/sender_auth/senders/new
2. Add/verify: `adityapandey.dev.in@gmail.com`
3. Check your Gmail inbox for verification email
4. Click the verification link
5. Status should show "Verified" ✅

**Without verification, emails will NOT be sent!**

## Step 3: Check SendGrid Activity Log

1. Go to: https://app.sendgrid.com/activity
2. Look for recent email attempts
3. Check status:
   - ✅ **Delivered** = Email was sent successfully
   - ❌ **Bounced** = Email address invalid
   - ❌ **Dropped** = Email blocked (check reason)
   - ❌ **Deferred** = Temporary issue, will retry
   - ❌ **Blocked** = SendGrid blocked it (check reason)

## Step 4: Test Email on Render

### Method 1: Use Management Command (Best)

1. Go to **Render Dashboard** → Your Service → **Shell** tab
2. Run:
   ```bash
   python manage.py test_sendgrid_email kingsong7060@gmail.com
   ```
3. Check output for success/error messages

### Method 2: Check Render Logs

1. Go to **Render Dashboard** → Your Service → **Logs** tab
2. Look for:
   - `✅ SendGrid email configuration loaded`
   - `✅ Email sent successfully` 
   - Or error messages like:
     - `Authentication failed`
     - `Network unreachable`
     - `Connection timeout`

### Method 3: Test via Registration

1. Visit: https://student-tracking-system-e1hq.onrender.com/register/student/
2. Register with: `kingsong7060@gmail.com`
3. Check:
   - Render logs for email status
   - Your inbox (and spam folder)
   - On-screen OTP code if email fails

## Step 5: Common Issues & Fixes

### Issue 1: "Authentication failed"
**Fix**: 
- Verify SENDGRID_API_KEY is correct
- Check API key hasn't been revoked in SendGrid
- Ensure EMAIL_HOST_USER = `apikey` (exact string)

### Issue 2: "Sender email not verified"
**Fix**:
- Go to SendGrid → Settings → Sender Authentication
- Verify `adityapandey.dev.in@gmail.com`
- Check Gmail inbox for verification email

### Issue 3: "Network unreachable" or "Connection timeout"
**Fix**:
- Render free tier might have restrictions
- Try increasing EMAIL_TIMEOUT to 30
- Check if SendGrid API is accessible from Render

### Issue 4: Email sent but not received
**Fix**:
- Check spam/junk folder
- Check SendGrid activity log for delivery status
- Verify recipient email address is correct
- Check if Gmail is blocking emails from SendGrid

### Issue 5: API Key Invalid
**Fix**:
1. Go to: https://app.sendgrid.com/settings/api_keys
2. Verify key exists and has "Mail Send" permissions
3. If needed, create new key with "Full Access"
4. Update SENDGRID_API_KEY in Render environment

## Step 6: Verify SendGrid Setup Checklist

- [ ] SendGrid account created
- [ ] API key generated (starts with `SG.`)
- [ ] API key added to Render environment variables
- [ ] Sender email (`adityapandey.dev.in@gmail.com`) verified in SendGrid
- [ ] Render environment variables all set correctly
- [ ] Render service redeployed after adding env vars
- [ ] Tested via management command on Render
- [ ] Checked SendGrid activity log

## Step 7: Quick Test Script for Render

Run this in Render Shell to test:

```python
python manage.py shell
```

Then run:
```python
from django.core.mail import send_mail
from django.conf import settings
import os

print("Email Config:")
print(f"BACKEND: {settings.EMAIL_BACKEND}")
print(f"HOST: {settings.EMAIL_HOST}")
print(f"USER: {settings.EMAIL_HOST_USER}")
print(f"FROM: {settings.DEFAULT_FROM_EMAIL}")
print(f"SENDGRID_KEY: {'SET' if os.environ.get('SENDGRID_API_KEY') else 'NOT SET'}")

try:
    result = send_mail(
        subject='Test Email',
        message='This is a test',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['kingsong7060@gmail.com'],
        fail_silently=False
    )
    print(f"Email result: {result}")
except Exception as e:
    print(f"Error: {e}")
```

## 📧 Still Not Working?

If emails still aren't arriving after all checks:

1. **Check SendGrid Dashboard** → Activity → Filter by recipient
2. **Check Spam Folder** in Gmail
3. **Verify API Key** hasn't been rate-limited (free tier: 100 emails/day)
4. **Check Render Logs** for specific error messages
5. **Try different recipient email** to rule out recipient-specific issues

---

**Need Help?** Check SendGrid status: https://status.sendgrid.com/

