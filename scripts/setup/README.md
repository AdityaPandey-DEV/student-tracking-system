# Setup Scripts

Scripts for initial setup and configuration of the Student Tracking System.

## Available Scripts

- **`setup_sendgrid.py`** ⭐ **Recommended for Render** - Configure SendGrid email service (works on Render free tier)
- **`setup_gmail.py`** - Configure Gmail SMTP settings (works locally, blocked on Render free tier)
- **`update_gmail_password.py`** - Update Gmail App Password in .env file
- **`setup_free_ai.py`** - Configure free AI providers (Groq, Hugging Face)
- **`setup_demo.py`** - Setup demo data for testing
- **`quick_setup.py`** - Quick setup wizard for the entire system

## Email Setup Guide

### For Render Deployment (Recommended):
```bash
python scripts/setup/setup_sendgrid.py
```
- ✅ Works on Render free tier
- ✅ 100 emails/day free
- ✅ No SMTP blocking issues

### For Local Development:
```bash
python scripts/setup/setup_gmail.py
```
- ✅ Works locally
- ❌ Blocked on Render free tier

📖 **Full Render email setup guide:** See [docs/RENDER_EMAIL_SETUP.md](../../docs/RENDER_EMAIL_SETUP.md)

## Usage

Run from project root:
```bash
python scripts/setup/setup_sendgrid.py  # For Render
python scripts/setup/setup_gmail.py     # For local dev
```

