"""
Notification service for sending OTP and other messages.
Supports both SMS (Twilio) and Email notifications.
"""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

def send_otp_notification(identifier, otp_code, purpose='registration', method='email'):
    """
    Send OTP notification via email (FREE) or SMS.
    identifier: email address or phone number
    method: 'email' (default/free) or 'sms'
    Returns True if delivery succeeds.
    """
    success = False
    
    # For development: always show OTP in console and return success
    if settings.DEBUG:
        logger.info(f"OTP for {identifier}: {otp_code} (Purpose: {purpose}, Method: {method})")
        print(f"\n=== OTP NOTIFICATION ===")
        print(f"Method: {method.upper()}")
        print(f"To: {identifier}")
        print(f"OTP Code: {otp_code}")
        print(f"Purpose: {purpose}")
        print(f"======================\n")
        
        # Also try to send email, but don't fail if it doesn't work
        try:
            if method == 'email':
                send_otp_email(identifier, otp_code, purpose)
        except Exception as e:
            logger.warning(f"Email sending failed in development mode: {e}")
        
        return True  # Always return success in development
    
    # Production mode: actually try to send
    if method == 'email':
        # Use Email OTP (completely free)
        success = send_otp_email(identifier, otp_code, purpose)
    elif method == 'sms':
        # Use SMS OTP (requires Twilio setup)
        if hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID:
            success = send_otp_sms(identifier, otp_code, purpose)
        else:
            logger.warning("SMS requested but Twilio not configured")
    
    return success

def send_otp_sms(phone_number, otp_code, purpose='password_reset'):
    """Send OTP via SMS using Twilio."""
    try:
        # Only import Twilio if we're actually going to use it
        if not (hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID):
            logger.warning("Twilio not configured")
            return False
            
        from twilio.rest import Client
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        if purpose == 'password_reset':
            message_body = f"Your Enhanced Timetable System password reset OTP is: {otp_code}. This code expires in 10 minutes."
        else:
            message_body = f"Your Enhanced Timetable System verification code is: {otp_code}. This code expires in 10 minutes."
        
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        logger.info(f"SMS sent successfully to {phone_number}. Message SID: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False

def send_otp_email(email, otp_code, purpose='password_reset'):
    """Send OTP via email."""
    try:
        if purpose == 'password_reset':
            subject = "Enhanced Timetable System - Password Reset OTP"
            template = 'emails/password_reset_otp.html'
        else:
            subject = "Enhanced Timetable System - Verification Code"
            template = 'emails/verification_otp.html'
        
        context = {
            'otp_code': otp_code,
            'purpose': purpose,
            'expires_minutes': 10
        }
        
        html_message = render_to_string(template, context)
        plain_message = f"Your OTP verification code is: {otp_code}. This code expires in 10 minutes."
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Email sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        return False

def send_announcement_notification(users, announcement):
    """Send announcement notification to users."""
    success_count = 0
    
    for user in users:
        try:
            # You could implement email or SMS notifications here
            # For now, we'll just log it
            logger.info(f"Announcement '{announcement.title}' sent to user {user.username}")
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send announcement to {user.username}: {str(e)}")
    
    return success_count
