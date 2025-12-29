#!/usr/bin/env python
"""
Test SendGrid and Twilio credentials
"""
import os

# Test SendGrid
print("=" * 50)
print("TESTING SENDGRID")
print("=" * 50)

sendgrid_key = "vFRgmvcwFIecwoBc3sLFq0r0kKAp8uvW"  # Your SendGrid secret

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    
    print(f"SendGrid Key length: {len(sendgrid_key)}")
    print(f"SendGrid Key starts with: {sendgrid_key[:5]}")
    
    message = Mail(
        from_email='shivorganicdairyfarms@gmail.com',
        to_emails='shivorganicdairyfarms@gmail.com',  # Test email
        subject='Test Email',
        plain_text_content='This is a test email'
    )
    
    sg = SendGridAPIClient(sendgrid_key)
    response = sg.send(message)
    
    print(f"✅ SendGrid SUCCESS! Status: {response.status_code}")
except Exception as e:
    print(f"❌ SendGrid FAILED: {str(e)}")
    if "401" in str(e):
        print("   → API key is wrong or expired")
    elif "403" in str(e):
        print("   → Sender email not verified in SendGrid")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("TESTING TWILIO")
print("=" * 50)

# Get from environment variables for security
import os
account_sid = os.environ.get('TWILIO_ACCOUNT_SID', 'YOUR_TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN', 'YOUR_TWILIO_AUTH_TOKEN')
messaging_service_sid = os.environ.get('TWILIO_MESSAGING_SERVICE_SID', 'YOUR_MESSAGING_SERVICE_SID')

try:
    from twilio.rest import Client
    
    print(f"Account SID: {account_sid[:4]}... (length: {len(account_sid)})")
    print(f"Auth Token: {auth_token[:4]}... (length: {len(auth_token)})")
    
    client = Client(account_sid, auth_token)
    
    # Test by fetching account info
    account = client.api.accounts(account_sid).fetch()
    
    print(f"✅ Twilio SUCCESS! Account: {account.friendly_name}")
    print(f"   Status: {account.status}")
    
    # Try to send a test WhatsApp
    try:
        test_message = client.messages.create(
            body="Test message from Shiv Dairy",
            messaging_service_sid=messaging_service_sid,
            to="whatsapp:+919158019119"  # Your test number
        )
        print(f"✅ WhatsApp test sent! SID: {test_message.sid}")
    except Exception as e:
        print(f"⚠️ WhatsApp send failed: {str(e)}")
        print("   (This is OK - might be sandbox or number issues)")
        
except Exception as e:
    print(f"❌ Twilio FAILED: {str(e)}")
    if "401" in str(e):
        print("   → Account SID or Auth Token is wrong")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("DONE")
print("=" * 50)

