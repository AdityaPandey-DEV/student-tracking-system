"""
SendGrid HTTP API Email Backend for Django
Uses SendGrid's HTTP API instead of SMTP - works reliably on Render free tier
"""

from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.warning("sendgrid package not installed. Install with: pip install sendgrid")


class SendGridBackend(BaseEmailBackend):
    """
    SendGrid HTTP API email backend.
    Uses SendGrid's REST API instead of SMTP - much more reliable on platforms like Render.
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        
        if not SENDGRID_AVAILABLE:
            raise ImportError("sendgrid package is required. Install with: pip install sendgrid")
        
        # Get API key from settings or environment
        self.api_key = getattr(settings, 'SENDGRID_API_KEY', None) or os.environ.get('SENDGRID_API_KEY')
        
        if not self.api_key:
            if not fail_silently:
                raise ValueError("SENDGRID_API_KEY not found in settings or environment variables")
            logger.error("SENDGRID_API_KEY not configured")
            self.api_key = None
        
        # Initialize SendGrid client
        if self.api_key:
            try:
                self.sg = SendGridAPIClient(self.api_key)
                logger.info("✅ SendGrid API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid client: {e}")
                self.sg = None
        else:
            self.sg = None
    
    def send_messages(self, email_messages):
        """Send one or more EmailMessage objects using SendGrid API."""
        if not self.sg:
            if not self.fail_silently:
                raise ValueError("SendGrid client not initialized")
            return 0
        
        num_sent = 0
        for message in email_messages:
            try:
                # Get from email
                from_email = message.from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
                
                # Extract HTML and plain text content from Django EmailMessage
                html_content = None
                plain_text_content = message.body
                
                # Check if message has HTML alternatives
                if hasattr(message, 'alternatives') and message.alternatives:
                    for content, mimetype in message.alternatives:
                        if mimetype == 'text/html':
                            html_content = content
                            break
                    # If no HTML found in alternatives, check if body is HTML
                    if not html_content:
                        # Try to detect if body is HTML
                        if '<html' in message.body.lower() or '<body' in message.body.lower():
                            html_content = message.body
                        else:
                            # Use body as plain text if no HTML detected
                            plain_text_content = message.body
                else:
                    # Check if body is HTML
                    if '<html' in message.body.lower() or '<body' in message.body.lower():
                        html_content = message.body
                        plain_text_content = None  # Will extract text from HTML if needed
                    else:
                        plain_text_content = message.body
                
                # Log email details for debugging
                logger.info(f"📧 Sending email via SendGrid API:")
                logger.info(f"   From: {from_email}")
                logger.info(f"   To: {message.to}")
                logger.info(f"   Subject: {message.subject}")
                logger.info(f"   Has HTML: {html_content is not None}")
                
                # Build SendGrid Mail object
                mail = Mail(
                    from_email=from_email,
                    to_emails=message.to,
                    subject=message.subject,
                    html_content=html_content or plain_text_content,
                    plain_text_content=plain_text_content if plain_text_content else "Please enable HTML to view this email."
                )
                
                # Add CC and BCC if present
                if message.cc:
                    mail.add_cc(message.cc)
                if message.bcc:
                    mail.add_bcc(message.bcc)
                
                # Add reply-to if present
                if message.reply_to:
                    mail.reply_to = message.reply_to[0] if isinstance(message.reply_to, list) else message.reply_to
                
                # Send email via SendGrid API
                response = self.sg.send(mail)
                
                # Check response status
                if response.status_code in [200, 201, 202]:
                    logger.info(f"✅ Email sent successfully via SendGrid API to {message.to}")
                    logger.info(f"   SendGrid response: {response.status_code} - {response.body}")
                    num_sent += 1
                else:
                    error_msg = f"SendGrid API returned status {response.status_code}: {response.body}"
                    logger.error(f"❌ Failed to send email: {error_msg}")
                    logger.error(f"   From: {from_email}, To: {message.to}")
                    if not self.fail_silently:
                        raise Exception(error_msg)
                        
            except Exception as e:
                logger.error(f"❌ Error sending email via SendGrid API: {str(e)}")
                if not self.fail_silently:
                    raise
                # Continue to next message
        
        return num_sent

