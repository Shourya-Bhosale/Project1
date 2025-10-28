#!/usr/bin/env python
"""
Test email configuration - Tests SMTP with proper backend
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shivdairy.settings')
django.setup()

from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings

print("=" * 60)
print("SMTP Email Configuration Test")
print("=" * 60)
print(f"Host: {settings.EMAIL_HOST}")
print(f"Port: {settings.EMAIL_PORT}")
print(f"User: {settings.EMAIL_HOST_USER}")
print(f"Password configured: {'Yes' if settings.EMAIL_HOST_PASSWORD else 'No'}")
print(f"Password length: {len(settings.EMAIL_HOST_PASSWORD)} chars")
print(f"Use TLS: {settings.EMAIL_USE_TLS}")
print(f"Timeout: {settings.EMAIL_TIMEOUT}s")
print()

# Test email with explicit SMTP backend
try:
    print("Creating SMTP backend connection...")
    smtp_backend = EmailBackend(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        timeout=settings.EMAIL_TIMEOUT,
    )
    
    print("Attempting to send test email...")
    email = EmailMessage(
        subject='Test Email from Shiv Dairy - SMTP Test',
        body='This is a test email to verify SMTP configuration.\n\nIf you receive this, SMTP is working correctly!',
        from_email=settings.EMAIL_HOST_USER,
        to=['shivorganicdairyfarms@gmail.com'],
        connection=smtp_backend
    )
    
    email.send()
    print("[SUCCESS] Email sent successfully via SMTP!")
    
    # Close the connection
    smtp_backend.close()
    print("[OK] SMTP connection closed properly")
    print("\n" + "="*60)
    print("TEST PASSED: Email configuration is working correctly!")
    print("Check your inbox: shivorganicdairyfarms@gmail.com")
    print("="*60)
    
except Exception as e:
    print(f"[ERROR] Error sending email: {str(e)}")
    print()
    print("Common issues:")
    print("1. EMAIL_HOST_PASSWORD not set or incorrect - get a Gmail App Password (16 chars)")
    print("2. Two-factor authentication not enabled on Gmail")
    print("3. Firewall blocking SMTP port 587")
    print("4. Incorrect email credentials")
    print()
    print(f"Current password length: {len(settings.EMAIL_HOST_PASSWORD)} chars (should be 16)")
    import traceback
    traceback.print_exc()

