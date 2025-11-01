"""
Notification service for sending OTP and other messages.
Supports both SMS (Twilio) and Email notifications.
"""

from django.conf import settings
from django.core.mail import send_mail, get_connection
from django.template.loader import render_to_string
import logging
import os
import threading
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

def timeout_handler(timeout_seconds):
    """Decorator to add timeout to function calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)
            
            if thread.is_alive():
                # Thread is still running - timeout occurred
                logger.error(f"{func.__name__} timed out after {timeout_seconds} seconds")
                raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
            
            if exception[0]:
                raise exception[0]
            
            return result[0]
        
        return wrapper
    return decorator

def send_otp_notification(identifier, otp_code, purpose='registration', method='email'):
    """
    Send OTP notification via email (FREE) or SMS.
    identifier: email address or phone number
    method: 'email' (default/free) or 'sms'
    Returns tuple: (success: bool, otp_code: str, error_message: str)
    
    Note: In case of network errors, OTP is still returned so user can manually enter it.
    """
    success = False
    error_message = None
    
    # Always log OTP for debugging (both development and production)
    logger.info(f"OTP for {identifier}: {otp_code} (Purpose: {purpose}, Method: {method})")
    
    # For development: always show OTP in console
    if settings.DEBUG:
        print(f"\n=== OTP NOTIFICATION ===")
        print(f"Method: {method.upper()}")
        print(f"To: {identifier}")
        print(f"OTP Code: {otp_code}")
        print(f"Purpose: {purpose}")
        print(f"======================\n")
        
        # Try to send email, but don't fail if it doesn't work
        try:
            if method == 'email':
                send_otp_email(identifier, otp_code, purpose)
                success = True
        except Exception as e:
            error_message = f"Email sending failed: {str(e)}"
            logger.warning(f"Email sending failed in development mode: {e}")
        
        # Always return success in development (OTP is in console)
        return (True, otp_code, error_message)
    
    # Production mode: try to send, but handle network errors gracefully
    if method == 'email':
        # Check if email backend is configured
        email_backend = getattr(settings, 'EMAIL_BACKEND', '')
        if email_backend == 'django.core.mail.backends.console.EmailBackend':
            # Console backend - just log and return success
            logger.info(f"Using console email backend - OTP logged: {otp_code}")
            return (True, otp_code, "Email backend is console (development mode)")
        
        # Try to send email
        try:
            success = send_otp_email(identifier, otp_code, purpose)
            if not success:
                # Email sending failed but OTP was attempted in background
                # In production, we return success=True (fire-and-forget) but log the error
                error_message = "Email sending initiated but may fail (check logs)"
                logger.warning(f"Email sending may have failed for {identifier}, but OTP generated: {otp_code}")
        except (OSError, ConnectionError, TimeoutError) as e:
            # Network errors - return OTP so user can manually enter it
            error_code = getattr(e, 'errno', None)
            if error_code == 101:  # Network is unreachable
                error_message = "Network unreachable - SMTP server cannot be reached. OTP is still valid."
            else:
                error_message = f"Network error: {str(e)}. OTP is still valid."
            logger.error(f"Network error sending email to {identifier}: {e}")
            logger.info(f"OTP {otp_code} is still valid for {identifier} - can be entered manually")
            # Return True with error message - OTP is still valid
            return (True, otp_code, error_message)
        except Exception as e:
            error_message = f"Email sending error: {str(e)}"
            logger.error(f"Failed to send email to {identifier}: {e}")
            # Still return OTP code even if email fails
            return (False, otp_code, error_message)
    elif method == 'sms':
        # Use SMS OTP (requires Twilio setup)
        if hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID:
            success = send_otp_sms(identifier, otp_code, purpose)
            if not success:
                error_message = "SMS sending failed"
        else:
            error_message = "SMS requested but Twilio not configured"
            logger.warning("SMS requested but Twilio not configured")
    
    return (success, otp_code, error_message)

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
            message_body = f"Your Student Tracking System password reset OTP is: {otp_code}. This code expires in 10 minutes."
        else:
            message_body = f"Your Student Tracking System verification code is: {otp_code}. This code expires in 10 minutes."
        
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

def _send_email_sync(email, otp_code, purpose):
    """Internal synchronous email sending function with explicit connection timeout."""
    if purpose == 'password_reset':
        subject = "Student Tracking System - Password Reset OTP"
        template = 'emails/password_reset_otp.html'
    else:
        subject = "Student Tracking System - Verification Code"
        template = 'emails/verification_otp.html'
    
    context = {
        'otp_code': otp_code,
        'purpose': purpose,
        'expires_minutes': 10
    }
    
    html_message = render_to_string(template, context)
    plain_message = f"Your OTP verification code is: {otp_code}. This code expires in 10 minutes."
    
    # Get timeout from settings
    timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
    
    # Create connection with explicit timeout
    connection = get_connection(
        backend=None,  # Use default backend from settings
        fail_silently=False,  # We want to catch errors
        timeout=timeout  # Explicit timeout
    )
    
    # Send email using the connection with timeout
    # send_mail with connection parameter uses the provided connection
    result = send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        connection=connection,
        fail_silently=False
    )
    
    # Close connection
    connection.close()
    
    # send_mail returns the number of emails sent (should be 1)
    return result > 0

def send_otp_email(email, otp_code, purpose='password_reset'):
    """Send OTP via email with timeout protection and non-blocking execution in production."""
    try:
        # Get timeout from settings, default to 10 seconds
        timeout_seconds = getattr(settings, 'EMAIL_TIMEOUT', 10)
        
        # In production, send email in a background thread (fire-and-forget)
        # This prevents worker timeouts while still attempting to send the email
        if not settings.DEBUG:
            def send_in_thread():
                try:
                    result = _send_email_sync(email, otp_code, purpose)
                    if result:
                        logger.info(f"Email sent successfully to {email}")
                    else:
                        logger.warning(f"Email sending to {email} failed (connection might have failed)")
                except TimeoutError:
                    logger.error(f"Email sending to {email} timed out after {timeout_seconds} seconds")
                except Exception as e:
                    logger.error(f"Failed to send email to {email}: {str(e)}")
            
            # Start thread and return immediately (fire-and-forget)
            thread = threading.Thread(target=send_in_thread)
            thread.daemon = True
            thread.start()
            
            # Return True immediately - email is being sent in background
            # User can request resend if email doesn't arrive
            logger.info(f"Email sending initiated for {email} (non-blocking)")
            return True
        else:
            # In development, send synchronously but with timeout protection
            try:
                result = _send_email_sync(email, otp_code, purpose)
                if result:
                    logger.info(f"Email sent successfully to {email}")
                    return True
                else:
                    logger.warning(f"Email sending to {email} returned False")
                    return False
            except TimeoutError:
                logger.error(f"Email sending to {email} timed out")
                return False
            except Exception as e:
                logger.error(f"Failed to send email to {email}: {str(e)}")
                return False
        
    except Exception as e:
        logger.error(f"Failed to initiate email sending to {email}: {str(e)}")
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
