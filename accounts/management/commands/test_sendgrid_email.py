"""
Management command to test SendGrid email sending.
Usage: python manage.py test_sendgrid_email kingsong7060@gmail.com
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail, get_connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Test SendGrid email sending to a specific email address'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address to send test email to (e.g., kingsong7060@gmail.com)'
        )

    def handle(self, *args, **options):
        recipient_email = options['email']
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('📧 TESTING SENDGRID EMAIL CONFIGURATION'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        # Display configuration
        self.stdout.write('📋 Current Email Configuration:')
        self.stdout.write(f'   EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'   EMAIL_PROVIDER: {getattr(settings, "EMAIL_PROVIDER", "Not set")}')
        self.stdout.write(f'   EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'   EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'   EMAIL_TIMEOUT: {getattr(settings, "EMAIL_TIMEOUT", "Not set")}')
        
        # Check SendGrid
        sendgrid_key = getattr(settings, 'SENDGRID_API_KEY', None)
        if sendgrid_key:
            self.stdout.write(self.style.SUCCESS(f'   SENDGRID_API_KEY: ✅ SET (length: {len(sendgrid_key)})'))
        else:
            self.stdout.write(self.style.ERROR('   SENDGRID_API_KEY: ❌ NOT SET'))
        
        self.stdout.write('\n' + '-'*70 + '\n')
        
        # Test connection
        try:
            self.stdout.write('📡 Testing SMTP connection...')
            connection = get_connection(
                backend=settings.EMAIL_BACKEND,
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=getattr(settings, 'EMAIL_HOST_PASSWORD', None),
                use_tls=settings.EMAIL_USE_TLS,
                timeout=getattr(settings, 'EMAIL_TIMEOUT', 10),
            )
            
            connection.open()
            self.stdout.write(self.style.SUCCESS('   ✅ Connection opened successfully!'))
            connection.close()
            self.stdout.write(self.style.SUCCESS('   ✅ Connection closed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Connection failed: {str(e)}'))
            self.stdout.write(self.style.WARNING('\n⚠️  Cannot proceed with email test due to connection error.'))
            return
        
        self.stdout.write('\n' + '-'*70 + '\n')
        
        # Send test email
        try:
            self.stdout.write(f'📤 Sending test email to: {recipient_email}')
            
            subject = '🧪 Test Email - Student Tracking System'
            message = f"""
Hello!

This is a test email from the Student Tracking System.

If you received this email, your SendGrid email configuration is working correctly!

Email Configuration:
- Backend: {settings.EMAIL_BACKEND}
- Provider: {getattr(settings, "EMAIL_PROVIDER", "N/A")}
- Host: {settings.EMAIL_HOST}
- From: {settings.DEFAULT_FROM_EMAIL}

Best regards,
Student Tracking System
            """
            
            result = send_mail(
                subject=subject,
                message=message.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
                connection=connection
            )
            
            if result == 1:
                self.stdout.write(self.style.SUCCESS('\n' + '='*70))
                self.stdout.write(self.style.SUCCESS('✅ SUCCESS! Email sent successfully!'))
                self.stdout.write(self.style.SUCCESS('='*70))
                self.stdout.write(f'\n📬 Please check the inbox (and spam folder) of: {recipient_email}')
                self.stdout.write('\n✅ Your email configuration is working correctly!')
                self.stdout.write('✅ Users can now register and receive OTP emails!')
            else:
                self.stdout.write(self.style.WARNING(f'\n⚠️  Email send returned: {result} (expected 1)'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR('\n' + '='*70))
            self.stdout.write(self.style.ERROR('❌ FAILED! Email sending error'))
            self.stdout.write(self.style.ERROR('='*70))
            self.stdout.write(self.style.ERROR(f'\nError: {type(e).__name__}: {str(e)}'))
            
            # Provide troubleshooting hints
            self.stdout.write('\n🔧 Troubleshooting:')
            if 'authentication' in str(e).lower() or '535' in str(e):
                self.stdout.write('   1. Verify your SendGrid API key is correct')
                self.stdout.write('   2. Check that the API key has "Mail Send" permissions')
            elif 'timeout' in str(e).lower():
                self.stdout.write('   1. Check network connectivity')
                self.stdout.write('   2. Verify EMAIL_TIMEOUT setting (should be 10 or higher)')
            elif 'connection' in str(e).lower():
                self.stdout.write('   1. Verify EMAIL_HOST is set to smtp.sendgrid.net')
                self.stdout.write('   2. Check firewall/network restrictions')
            else:
                self.stdout.write('   1. Check SendGrid dashboard for any errors')
                self.stdout.write('   2. Verify sender email is verified in SendGrid')
                self.stdout.write('   3. Check Render logs for additional details')
            
            self.stdout.write(f'\n📋 Full error: {str(e)}')

