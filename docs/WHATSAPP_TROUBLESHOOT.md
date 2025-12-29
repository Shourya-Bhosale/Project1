# WhatsApp Not Sending - Troubleshooting

## Common Issues:

### 1. Twilio Sandbox Requirement
- Customer must send "join [keyword]" to Twilio sandbox number first
- Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
- See the keyword (e.g., "pizza", "orange")
- Customer sends "join [keyword]" to +1 415 523 8886
- After that, messages will work

### 2. Check Render Logs
Look for these messages:
- `📱 Attempting WhatsApp to...` - Shows it's trying
- `✅ WhatsApp sent to...` - Success
- `❌ WhatsApp error:` - Failure with reason

### 3. Phone Number Format
The code automatically formats to:
- `whatsapp:+919158019119` (for Indian numbers)
- Make sure phone number is correct

### 4. Twilio Trial Account Limits
- Trial accounts can only message verified numbers
- Need to verify customer's number in Twilio console

## Quick Fix:
1. Check Render logs for exact error
2. Ensure customer joined Twilio sandbox
3. Verify phone number is correct

