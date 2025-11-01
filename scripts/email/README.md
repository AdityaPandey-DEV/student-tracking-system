# 📧 Email Utility Scripts

This directory contains utility scripts for email testing and configuration.

## 📋 Scripts

### Configuration Checkers
- **check_email_config.py** - Check email configuration from environment variables (no Django required)

### Testing Scripts
- **test_email_now.py** - Quick email test script
- **test_email_sendgrid.py** - Comprehensive SendGrid email test

## 🚀 Usage

### Check Email Configuration (Local)
```bash
python scripts/email/check_email_config.py
```

### Test Email (Requires Django)
```bash
python scripts/email/test_email_now.py
# OR
python scripts/email/test_email_sendgrid.py
```

### Test Email on Render
```bash
python manage.py test_sendgrid_email your-email@example.com
```

## 📝 Related Documentation

See `docs/email/` for comprehensive email setup and troubleshooting guides.

