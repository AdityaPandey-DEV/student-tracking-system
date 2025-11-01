#!/usr/bin/env python
"""
Debug OTP Status and Timezone Settings
=====================================
This script helps debug OTP expiration issues by checking:
1. Current server time vs database time
2. Active OTPs and their expiration status
3. Timezone configuration
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
# Add project root to path (go up 2 directories from scripts/debug/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
django.setup()

from django.utils import timezone
from django.conf import settings
from accounts.models import EmailOTP

def debug_otp_system():
    print("🔍 OTP System Debug Information")
    print("=" * 50)
    
    # Check timezone settings
    print(f"📅 Django TIME_ZONE: {settings.TIME_ZONE}")
    print(f"🌐 USE_TZ: {settings.USE_TZ}")
    print(f"⏰ Current timezone-aware time: {timezone.now()}")
    print(f"⏰ Current naive time: {datetime.now()}")
    print()
    
    # Check active OTPs
    print("📧 Active Email OTPs:")
    print("-" * 30)
    
    active_otps = EmailOTP.objects.filter(
        is_used=False,
        expires_at__gt=timezone.now()
    ).order_by('-created_at')
    
    if active_otps:
        for otp in active_otps:
            time_left = otp.expires_at - timezone.now()
            print(f"✅ {otp.email}: {otp.otp_code} ({otp.purpose})")
            print(f"   Created: {otp.created_at}")
            print(f"   Expires: {otp.expires_at}")
            print(f"   Time left: {time_left}")
            print()
    else:
        print("ℹ️  No active OTPs found")
    
    # Check expired OTPs
    print("⚰️  Recently Expired Email OTPs:")
    print("-" * 35)
    
    expired_otps = EmailOTP.objects.filter(
        is_used=False,
        expires_at__lte=timezone.now(),
        created_at__gte=timezone.now() - timedelta(hours=1)
    ).order_by('-created_at')
    
    if expired_otps:
        for otp in expired_otps:
            time_expired = timezone.now() - otp.expires_at
            print(f"❌ {otp.email}: {otp.otp_code} ({otp.purpose})")
            print(f"   Created: {otp.created_at}")
            print(f"   Expired: {otp.expires_at}")
            print(f"   Expired since: {time_expired}")
            print()
    else:
        print("ℹ️  No recently expired OTPs found")
    
    # Check used OTPs
    print("✅ Recently Used Email OTPs:")
    print("-" * 30)
    
    used_otps = EmailOTP.objects.filter(
        is_used=True,
        created_at__gte=timezone.now() - timedelta(hours=1)
    ).order_by('-created_at')
    
    if used_otps:
        for otp in used_otps[:5]:  # Show last 5
            print(f"✅ {otp.email}: {otp.otp_code} ({otp.purpose})")
            print(f"   Created: {otp.created_at}")
            print(f"   Expires: {otp.expires_at}")
            print()
    else:
        print("ℹ️  No recently used OTPs found")

def test_otp_generation_and_verification():
    print("\n🧪 Testing OTP Generation & Verification")
    print("=" * 50)
    
    test_email = "test@example.com"
    
    # Generate test OTP
    print(f"📧 Generating OTP for: {test_email}")
    otp_code = EmailOTP.generate_otp(test_email, 'registration')
    print(f"📝 Generated OTP: {otp_code}")
    
    # Check database entry
    otp_obj = EmailOTP.objects.filter(email=test_email, is_used=False).first()
    if otp_obj:
        print(f"💾 Database Entry:")
        print(f"   Email: {otp_obj.email}")
        print(f"   Code: {otp_obj.otp_code}")
        print(f"   Purpose: {otp_obj.purpose}")
        print(f"   Created: {otp_obj.created_at}")
        print(f"   Expires: {otp_obj.expires_at}")
        print(f"   Is Used: {otp_obj.is_used}")
        
        # Test immediate verification
        print(f"\n🔐 Testing immediate verification...")
        is_valid = EmailOTP.verify_otp(test_email, otp_code, 'registration')
        print(f"✅ Verification result: {is_valid}")
        
        if is_valid:
            print("🎉 OTP system working correctly!")
        else:
            print("❌ OTP verification failed - check timezone/database issues")
    
    else:
        print("❌ Failed to find OTP in database")

if __name__ == "__main__":
    debug_otp_system()
    test_otp_generation_and_verification()
    
    print("\n" + "="*50)
    print("🔧 Recommendations:")
    print("1. OTPs now expire after 15 minutes (was 10)")
    print("2. Session timeout extended to 30 minutes")
    print("3. Better error messages for duplicate registrations")
    print("4. Clear session data immediately on success/failure")
    print("5. Check Render environment variables for EMAIL_HOST_PASSWORD spaces")
