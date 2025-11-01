# 🔧 Set SendGrid Environment Variables on Render

## ⚠️ IMPORTANT SECURITY NOTE
**DO NOT** commit API keys to git! These should only be set in Render's environment variables.

## Steps to Add Environment Variables on Render

### Step 1: Go to Render Dashboard
1. Visit: https://dashboard.render.com
2. Click on your service (e.g., `student-tracking-system`)

### Step 2: Add Environment Variables
1. Go to **Environment** tab
2. Click **"Add Environment Variable"** for each of these:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_PROVIDER=sendgrid
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
SENDGRID_API_KEY=SG.your-actual-sendgrid-api-key-here
DEFAULT_FROM_EMAIL=adityapandey.dev.in@gmail.com
EMAIL_TIMEOUT=10
```

### Step 3: Important Values
- **EMAIL_HOST_USER**: Must be exactly `apikey` (the literal string "apikey")
- **SENDGRID_API_KEY**: Your full API key starting with `SG.`
- **DEFAULT_FROM_EMAIL**: Must match a verified sender in SendGrid

### Step 4: Save and Redeploy
1. Click **"Save Changes"**
2. Render will automatically redeploy your service
3. Wait for deployment to complete

### Step 5: Verify Sender Email in SendGrid
**CRITICAL**: Before emails will work, you MUST verify the sender email:

1. Go to: https://app.sendgrid.com/settings/sender_auth/senders/new
2. Click **"Create New Sender"**
3. Enter:
   - **From Email**: `adityapandey.dev.in@gmail.com`
   - **From Name**: `Student Tracking System` (optional)
   - Fill in other required fields
4. Click **"Create"**
5. Check your Gmail inbox (`adityapandey.dev.in@gmail.com`) for verification email
6. Click the verification link
7. Status should change to "Verified" ✅

### Step 6: Test Email
After deployment completes, test email sending:

**On Render Dashboard → Shell tab:**
```bash
python manage.py test_sendgrid_email kingsong7060@gmail.com
```

Or run:
```bash
python test_email_now.py
```

## ✅ Verification Checklist

- [ ] All environment variables added to Render
- [ ] Service redeployed after adding variables
- [ ] Sender email verified in SendGrid dashboard
- [ ] Test email command run on Render
- [ ] Email received at kingsong7060@gmail.com (check spam folder)

## 🔍 If Email Still Doesn't Arrive

1. **Check SendGrid Activity Log**: https://app.sendgrid.com/activity
   - Look for email attempts
   - Check delivery status

2. **Check Render Logs**:
   - Look for `✅ SendGrid email configuration loaded`
   - Check for error messages

3. **Common Issues**:
   - Sender email not verified → Verify in SendGrid
   - API key incorrect → Check in Render environment
   - Spam folder → Check Gmail spam folder
   - Rate limit → Free tier allows 100 emails/day

---

**Remember**: Never commit API keys to git! Always use environment variables.

