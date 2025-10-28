#!/usr/bin/env python
"""
Test company WhatsApp notification configuration
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shivdairy.settings')
django.setup()

from django.conf import settings

print("Company WhatsApp Configuration Test")
print("=" * 50)

# Check if company WhatsApp phone is set
company_whatsapp = getattr(settings, 'COMPANY_WHATSAPP_PHONE', '').strip()
print(f"Company WhatsApp Phone: {company_whatsapp if company_whatsapp else '❌ NOT SET'}")
print()

# Check Twilio configuration
twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '').strip()
twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '').strip()
twilio_from = getattr(settings, 'TWILIO_WHATSAPP_FROM', '').strip()

print("Twilio Configuration:")
print(f"  Account SID: {'✅ Set' if twilio_sid and len(twilio_sid) > 10 else '❌ NOT SET'}")
print(f"  Auth Token: {'✅ Set' if twilio_token and len(twilio_token) > 30 else '❌ NOT SET'}")
print(f"  WhatsApp From: {twilio_from if twilio_from else '❌ NOT SET'}")
print()

# Overall status
if company_whatsapp and twilio_sid and twilio_token:
    print("✅ Configuration Complete!")
    print(f"   Orders will send WhatsApp notifications to: {company_whatsapp}")
    print()
    print("To test:")
    print("   1. Place a test order on your website")
    print("   2. Check WhatsApp at " + company_whatsapp)
    print("   3. You should receive a notification with order details")
else:
    print("❌ Configuration Incomplete!")
    print()
    if not company_whatsapp:
        print("Missing: COMPANY_WHATSAPP_PHONE")
        print("   Set it with: $env:COMPANY_WHATSAPP_PHONE='+919158019119'")
    if not twilio_sid:
        print("Missing: TWILIO_ACCOUNT_SID")
    if not twilio_token:
        print("Missing: TWILIO_AUTH_TOKEN")

