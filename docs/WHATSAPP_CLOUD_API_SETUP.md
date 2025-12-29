# WhatsApp Cloud API Setup Guide (Meta)

## Why WhatsApp Cloud API?
- ✅ **1,000 free messages/month** per WhatsApp Business number
- ✅ Can send to any users (no "join" step required)
- ✅ Works for notifications, confirmations, etc.
- ✅ Direct integration with Meta (Facebook)

## Step 1: Create Meta Business Account

1. Go to https://business.facebook.com/
2. Create a Meta Business Account (if you don't have one)
3. Verify your business information

## Step 2: Set Up WhatsApp Business Account

1. In Meta Business Suite, go to **WhatsApp** section
2. Click **"Get Started"** with WhatsApp Business API
3. Follow the setup wizard to connect your WhatsApp Business number

## Step 3: Get Access Token & Phone Number ID

1. Go to **Meta Developers**: https://developers.facebook.com/
2. Create a new App (or use existing)
3. Add **"WhatsApp"** product to your app
4. Go to **WhatsApp → API Setup**

You'll see:
- **Phone number ID** (e.g., `123456789012345`)
- **Temporary access token** (or create a permanent one)

## Step 4: Get System User Access Token (Recommended for Production)

1. In Meta Business Suite, go to **Business Settings**
2. Navigate to **Users → System Users**
3. Create a new System User (or use existing)
4. Assign WhatsApp permissions
5. Generate a **System User Access Token**
   - Select your app
   - Select permissions: `whatsapp_business_messaging`, `whatsapp_business_management`
   - Generate token (can make it never expire)

## Step 5: Set Environment Variables

### Local Development (.env file):
```
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_API_VERSION=v18.0
COMPANY_WHATSAPP_PHONE=+919158019119
```

### Windows PowerShell:
```powershell
[System.Environment]::SetEnvironmentVariable('WHATSAPP_ACCESS_TOKEN', 'your_token', 'User')
[System.Environment]::SetEnvironmentVariable('WHATSAPP_PHONE_NUMBER_ID', 'your_id', 'User')
[System.Environment]::SetEnvironmentVariable('WHATSAPP_API_VERSION', 'v18.0', 'User')
```

### Production (Render/Heroku):
Add these environment variables in your hosting platform:
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_API_VERSION` (optional, defaults to v18.0)
- `COMPANY_WHATSAPP_PHONE` (your company number to receive notifications)

## Step 6: Verify Your Phone Number

1. In WhatsApp API Setup, you'll need to verify your business phone number
2. Follow the verification process (usually via SMS/Phone call)
3. Once verified, the phone number is ready to send messages

## Step 7: Test It

After setting environment variables:
1. Restart your Django server
2. Place a test order (COD or Razorpay)
3. Check console for `[SUCCESS] WhatsApp sent via Meta Cloud API!`
4. Check the recipient's WhatsApp

## Message Limits

- **Free Tier**: 1,000 messages/month
- **Paid Tier**: $0.005 to $0.01 per message (depends on country)

## Troubleshooting

### Error: 401 Unauthorized
- Check if `WHATSAPP_ACCESS_TOKEN` is correct
- Token might have expired (get a new one)
- Use System User Access Token for production

### Error: 404 Not Found
- Check if `WHATSAPP_PHONE_NUMBER_ID` is correct
- Verify the phone number is set up in Meta Business

### Error: 403 Forbidden
- Check if phone number has permission to send messages
- Verify phone number is verified in Meta Business

### Error: 429 Rate Limit
- You've exceeded 1,000 messages/month (free tier)
- Wait for next month or upgrade

## Benefits Over Twilio

1. **Free tier**: 1,000 messages/month (Twilio is pay-per-use)
2. **No sandbox**: Send to any number immediately
3. **Direct integration**: No third-party needed
4. **Better delivery**: Meta's own infrastructure

## API Documentation

- Official docs: https://developers.facebook.com/docs/whatsapp/cloud-api
- API Reference: https://developers.facebook.com/docs/whatsapp/cloud-api/reference

