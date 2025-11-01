# 🧪 Testing Email on Render

## ✅ Your Configuration is Ready!

Based on the configuration check, your SendGrid setup looks correct:
- ✅ EMAIL_BACKEND: SMTP
- ✅ EMAIL_PROVIDER: sendgrid
- ✅ EMAIL_HOST: smtp.sendgrid.net
- ✅ SENDGRID_API_KEY: Valid (starts with 'SG.')
- ✅ DEFAULT_FROM_EMAIL: adityapandey.dev.in@gmail.com

## 🚀 How to Test Email Sending

### Option 1: Test via Registration (Recommended)
1. Go to your Render app: `https://student-tracking-system-e1hq.onrender.com/register/student/`
2. Fill in the registration form with email: `kingsong7060@gmail.com`
3. Submit the form
4. Check:
   - Render logs for email sending status
   - Your email inbox (and spam folder) for the OTP email
   - If email fails, the OTP code will be displayed on screen

### Option 2: Test via Django Management Command

**On Render Dashboard:**
1. Go to your service → **Shell** tab
2. Run:
   ```bash
   python manage.py test_sendgrid_email kingsong7060@gmail.com
   ```

This will:
- Display your email configuration
- Test the SMTP connection
- Send a test email to kingsong7060@gmail.com
- Show success/failure status

### Option 3: Test via Django Shell (Alternative)

**On Render Dashboard:**
1. Go to your service → **Shell** tab
2. Run:
   ```python
   python manage.py shell
   ```
3. In the shell:
   ```python
   from django.core.mail import send_mail
   from django.conf import settings
   
   send_mail(
       subject='Test Email',
       message='This is a test email from Render',
       from_email=settings.DEFAULT_FROM_EMAIL,
       recipient_list=['kingsong7060@gmail.com'],
       fail_silently=False
   )
   ```

## 📋 What to Check

After testing:
1. **Render Logs**: Look for:
   - `✅ SendGrid email configuration loaded`
   - `✅ Email sent successfully` (or error messages)

2. **Email Inbox**: Check:
   - Inbox of `kingsong7060@gmail.com`
   - Spam/Junk folder
   - Check email arrived within 1-2 minutes

3. **If Email Fails**:
   - Check Render logs for specific error
   - Verify SendGrid API key in Render environment variables
   - Verify sender email (adityapandey.dev.in@gmail.com) is verified in SendGrid
   - Check SendGrid dashboard for any blocks/errors

## 🔍 Troubleshooting

### Email Not Arriving?
1. Check spam folder
2. Verify sender email is verified in SendGrid dashboard
3. Check SendGrid activity log: https://app.sendgrid.com/activity
4. Verify API key has "Mail Send" permissions

### Connection Errors?
1. Check Render logs for network errors
2. Verify EMAIL_HOST is `smtp.sendgrid.net`
3. Check EMAIL_TIMEOUT is set (should be 10 or higher)

### Authentication Errors?
1. Verify SENDGRID_API_KEY is correct (starts with 'SG.')
2. Check API key hasn't been revoked in SendGrid
3. Ensure EMAIL_HOST_USER is set to literal string 'apikey'

## 📧 Expected Result

If everything works, you should see:
- ✅ Test email arrives at kingsong7060@gmail.com
- ✅ OTP emails work during user registration
- ✅ No timeout errors in Render logs

---

**Note**: SendGrid free tier allows 100 emails/day. Monitor usage at: https://app.sendgrid.com/stats

