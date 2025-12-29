# Company WhatsApp Notification Setup

## Configuration

The company WhatsApp phone number has been configured in the system.

**Phone Number:** +919158019119

## To Enable in Your Environment

### Option 1: Create a `.env` file (Recommended for local development)

Create a file named `.env` in the root directory (C:\Users\Adv Sandeep Bhosale\CB\) with:

```
COMPANY_WHATSAPP_PHONE=+919158019119
```

### Option 2: Set Environment Variable (Windows PowerShell)

For current session:
```powershell
$env:COMPANY_WHATSAPP_PHONE="+919158019119"
$env:TWILIO_ACCOUNT_SID="YOUR_TWILIO_ACCOUNT_SID"
$env:TWILIO_AUTH_TOKEN="YOUR_TWILIO_AUTH_TOKEN"
```

For permanent (all sessions):
```powershell
[System.Environment]::SetEnvironmentVariable('COMPANY_WHATSAPP_PHONE', '+919158019119', 'User')
[System.Environment]::SetEnvironmentVariable('TWILIO_ACCOUNT_SID', 'YOUR_TWILIO_ACCOUNT_SID', 'User')
[System.Environment]::SetEnvironmentVariable('TWILIO_AUTH_TOKEN', 'YOUR_TWILIO_AUTH_TOKEN', 'User')
```

### Option 3: For Production (Render/Heroku/etc.)

Add this environment variable in your hosting platform's dashboard:
- Variable Name: `COMPANY_WHATSAPP_PHONE`
- Variable Value: `+919158019119`

## Testing

Once configured, whenever a new order is placed, you will receive a WhatsApp message at **+919158019119** with complete order details.

## Important Notes

- Make sure the WhatsApp number is registered and active
- If using Twilio sandbox, the number needs to send "join [keyword]" to Twilio first
- The system will automatically try WhatsApp first, then fallback to email if WhatsApp fails

