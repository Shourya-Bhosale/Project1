# Gmail SMTP Setup Guide

This guide will help you configure Gmail SMTP to send emails reliably.

## Quick Fix Applied ✅

I've fixed the SMTP configuration with these improvements:

1. **SMTP Backend Always Available**: SMTP backend is now always configured, not just when SendGrid is missing
2. **Increased Timeout**: Changed from 5 seconds to 30 seconds for better reliability
3. **Proper Gmail Defaults**: Changed default to Gmail SMTP (`smtp.gmail.com`)
4. **Fixed Connection Handling**: Both customer and company emails now use proper SMTP backend
5. **Better Error Handling**: Improved error messages and traceback logging

## Step 1: Enable 2-Factor Authentication on Gmail

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** for your Gmail account
3. You'll need this to create an App Password

## Step 2: Generate Gmail App Password

1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" as the app
3. Select "Other" as the device and type "Shiv Dairy App"
4. Click "Generate"
5. Copy the 16-character password (will look like: `abcd efgh ijkl mnop`)

## Step 3: Set Environment Variable

### Windows (PowerShell):
```powershell
[System.Environment]::SetEnvironmentVariable('EMAIL_HOST_PASSWORD', 'your-16-char-app-password', 'User')
```

### Windows (Command Prompt):
```cmd
setx EMAIL_HOST_PASSWORD "your-16-char-app-password"
```

### Or add to .env file:
```
EMAIL_HOST_USER=shivorganicdairyfarms@gmail.com
EMAIL_HOST_PASSWORD=yourapppasswordhere
```

**Important**: 
- Remove spaces from the App Password if any
- The password should be 16 characters without spaces
- Example: If Gmail gives you `abcd efgh ijkl mnop`, use `abcdefghijklmnop`

## Step 4: Test SMTP Configuration

Run the test script:

```bash
python test_email.py
```

You should see:
```
✅ Email sent successfully via SMTP!
```

## Step 5: Restart Your Application

After setting the environment variable:
1. **Restart your terminal/IDE**
2. **Restart your Django server** (if running)
3. Test with an actual order

## Troubleshooting

### Issue: "SMTP authentication failed"

**Solution**: 
- Double-check the App Password (should be 16 chars, no spaces)
- Make sure 2-Factor Authentication is enabled
- Try regenerating the App Password

### Issue: "Connection timed out"

**Solution**:
- Check your firewall settings
- Ensure port 587 is not blocked
- Try using a different network

### Issue: "Email not sending but no error"

**Solution**:
- Check spam folder
- Verify EMAIL_HOST_USER is correct
- Look at Django console for error messages

## Alternative: Use Brevo or SendGrid API

If Gmail SMTP doesn't work, you can use API-based email services (which are more reliable):

1. **Brevo** (Free: 300 emails/day): Set `BREVO_API_KEY` environment variable
2. **SendGrid** (Free: 100 emails/day): Set `SENDGRID_API_KEY` environment variable

The code will automatically try API methods first, then fall back to SMTP.

## Current SMTP Settings

- **Host**: `smtp.gmail.com` (default, can be changed via `EMAIL_HOST`)
- **Port**: `587`
- **Use TLS**: `True`
- **Timeout**: `30` seconds
- **User**: `shivorganicdairyfarms@gmail.com` (default, set via `EMAIL_HOST_USER`)
- **Password**: Must be set via `EMAIL_HOST_PASSWORD`

## Verify Configuration

Check Django startup logs - you should see:
```
📧 SMTP Configuration:
   Host: smtp.gmail.com
   Port: 587
   User: shivorganicdairyfarms@gmail.com
   Password configured: Yes
   Password length: 16 chars
   Use TLS: True
   Timeout: 30s
✅ SMTP email backend ready
```

If you see "Password configured: No", the `EMAIL_HOST_PASSWORD` environment variable is not set.

