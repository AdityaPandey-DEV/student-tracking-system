# 📧 Email Setup for Render Free Tier

## ⚠️ Why Gmail SMTP Doesn't Work on Render Free Tier

Render's free tier **blocks outbound SMTP connections** to Gmail. This causes errors like:
- `[Errno 101] Network is unreachable`
- `Connection refused`
- `SMTPConnectError`

## ✅ Solution: Use SendGrid (Free)

SendGrid offers **100 emails/day for free** and works perfectly on Render's free tier.

---

## 🚀 Quick Setup Guide

### Step 1: Create SendGrid Account
1. Go to: https://signup.sendgrid.com/
2. Sign up for a free account
3. Verify your email address

### Step 2: Generate API Key
1. Go to: https://app.sendgrid.com/settings/api_keys
2. Click **"Create API Key"**
3. Name: `Student Tracking System`
4. Permissions: **Full Access**
5. Click **"Create & View"**
6. **Copy the API key immediately** (you'll only see it once!)
   - Format: `SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 3: Verify Sender Email
1. Go to: https://app.sendgrid.com/settings/sender_auth/senders/new
2. Enter your email address
3. Verify via email link
4. This email will be used as `DEFAULT_FROM_EMAIL`

### Step 4: Configure Render Environment Variables

In your **Render Dashboard** → **Environment** tab, add:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_PROVIDER=sendgrid
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
SENDGRID_API_KEY=SG.your-actual-api-key-here
DEFAULT_FROM_EMAIL=your-verified-email@example.com
EMAIL_TIMEOUT=10
```

**Important:**
- Replace `SG.your-actual-api-key-here` with your actual SendGrid API key
- Replace `your-verified-email@example.com` with your verified SendGrid email
- The `EMAIL_HOST_USER=apikey` is required for SendGrid (literal string "apikey")

### Step 5: Redeploy
After adding environment variables, trigger a redeploy in Render.

---

## 🧪 Testing

After deployment, test email sending:

1. **Try registering a new user**
2. **Check Render logs** for email sending status
3. **Check your SendGrid dashboard** → Activity Feed to see sent emails

---

## 📊 SendGrid Free Tier Limits

- **100 emails/day** (perfect for testing and small deployments)
- **Unlimited contacts**
- **All features included**

If you need more:
- **Upgrade to Essentials**: $19.95/month for 50,000 emails/month
- Or use multiple SendGrid accounts for different purposes

---

## 🔄 Alternative: Using Setup Script Locally

You can also use the setup script:

```bash
python scripts/setup/setup_sendgrid.py
```

This will:
1. Guide you through SendGrid setup
2. Update your local `.env` file
3. Show you Render configuration instructions

---

## 🆚 SendGrid vs Gmail SMTP

| Feature | Gmail SMTP | SendGrid |
|---------|------------|----------|
| Works on Render Free Tier | ❌ No | ✅ Yes |
| Free Tier Limit | Unlimited* | 100/day |
| Setup Complexity | Medium | Easy |
| API vs SMTP | SMTP only | Both available |
| Reliability | High | Very High |
| Best For | Local dev | Production |

\* Gmail SMTP works locally but is blocked on Render free tier

---

## 🔧 Troubleshooting

### "Network is unreachable" error
- ✅ Solution: Switch to SendGrid (see above)

### "Authentication failed" error
- Check that `EMAIL_HOST_USER=apikey` (literal string)
- Verify your `SENDGRID_API_KEY` is correct
- Ensure API key has "Full Access" permissions

### "Sender email not verified"
- Go to SendGrid → Sender Authentication
- Verify your sender email address
- Wait a few minutes after verification

### Emails not arriving
- Check SendGrid Activity Feed: https://app.sendgrid.com/activity
- Check spam folder
- Verify sender email is verified in SendGrid

---

## 📝 Environment Variables Reference

### Required for SendGrid:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_PROVIDER=sendgrid
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
SENDGRID_API_KEY=<your-api-key>
DEFAULT_FROM_EMAIL=<verified-email>
```

### Optional:
```env
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_TIMEOUT=10
```

---

## ✅ Checklist

- [ ] Created SendGrid account
- [ ] Generated API key with Full Access
- [ ] Verified sender email in SendGrid
- [ ] Added all environment variables to Render
- [ ] Triggered redeploy
- [ ] Tested email sending (user registration)
- [ ] Verified emails in SendGrid Activity Feed

---

## 🎉 Success!

Once configured, your app will send emails reliably on Render free tier!

Need help? Check SendGrid docs: https://docs.sendgrid.com/

