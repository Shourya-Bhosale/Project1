# API Setup Instructions

## SendGrid Email Setup

1. **Sign up for SendGrid**
   - Go to: https://signup.sendgrid.com/
   - Free tier: 100 emails/day

2. **Get API Key**
   - Login to SendGrid dashboard
   - Go to: Settings → API Keys
   - Click "Create API Key"
   - Give it a name (e.g., "Django App")
   - Select "Full Access" or "Restricted Access" → Mail Send
   - Copy the API key (you'll only see it once!)

3. **Add to Render**
   - Go to Render Dashboard → Your Service → Environment
   - Add variable: `SENDGRID_API_KEY` = `your_api_key_here`

## Twilio WhatsApp Setup

1. **Sign up for Twilio**
   - Go to: https://www.twilio.com/try-twilio
   - Free trial with $15.50 credit

2. **Get Credentials**
   - After signup, go to: https://console.twilio.com/
   - Copy your Account SID and Auth Token
   - These are visible on the dashboard homepage

3. **Set up WhatsApp Sandbox**
   - Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
   - Send "join <keyword>" to the sandbox number (shown on that page)
   - Example: Send "join pizza" to +1 415 523 8886
   - Save the sandbox number (it's in format `whatsapp:+14155238886`)

4. **Add to Render**
   - Go to Render Dashboard → Your Service → Environment
   - Add variables:
     - `TWILIO_ACCOUNT_SID` = `your_account_sid`
     - `TWILIO_AUTH_TOKEN` = `your_auth_token`
     - `TWILIO_WHATSAPP_FROM` = `whatsapp:+14155238886` (your sandbox number)

## Production Setup (Optional)

For production WhatsApp (not sandbox), you need to:
1. Get WhatsApp Business API access from Twilio
2. Set up your WhatsApp Business number
3. Update `TWILIO_WHATSAPP_FROM` to your business number

## Test It

After adding the environment variables on Render:
1. Restart your service
2. Place a test order
3. Check that both email and WhatsApp are sent

## Fallback

If SendGrid is not configured, the app will fallback to SMTP (which may not work on Render due to network restrictions).

