# Connect Your Existing WhatsApp Business Number

## Quick Setup for Existing WhatsApp Business Number

Since you already have a WhatsApp Business number, here's how to connect it:

## Step 1: Access Meta Business Suite

1. Go to **https://business.facebook.com/**
2. Log in with your Facebook account
3. Make sure your WhatsApp Business number is already connected

## Step 2: Get Your Phone Number ID

1. Go to **WhatsApp → API Setup** in Meta Business Suite
2. Find your WhatsApp Business number
3. Copy the **Phone Number ID** (looks like: `123456789012345`)
4. This is your `WHATSAPP_PHONE_NUMBER_ID`

## Step 3: Get Access Token

### Option A: Temporary Token (Quick Test)
1. In **WhatsApp → API Setup**, you'll see a **Temporary Access Token**
2. Copy it (expires in 1-24 hours)
3. Use for testing quickly

### Option B: Permanent System User Token (Recommended)
1. Go to **Business Settings → Users → System Users**
2. Create a new System User (or use existing)
3. Click **"Generate New Token"**
4. Select:
   - Your app
   - Expiration: **Never** (or long duration)
   - Permissions: `whatsapp_business_messaging`, `whatsapp_business_management`
5. Copy the generated token

## Step 4: Set Environment Variables

### Windows PowerShell:
```powershell
# Replace with YOUR actual values
[System.Environment]::SetEnvironmentVariable('WHATSAPP_ACCESS_TOKEN', 'YOUR_TOKEN_HERE', 'User')
[System.Environment]::SetEnvironmentVariable('WHATSAPP_PHONE_NUMBER_ID', 'YOUR_PHONE_NUMBER_ID', 'User')
[System.Environment]::SetEnvironmentVariable('WHATSAPP_API_VERSION', 'v18.0', 'User')
[System.Environment]::SetEnvironmentVariable('COMPANY_WHATSAPP_PHONE', '+919158019119', 'User')
```

### Or add to .env file:
```
WHATSAPP_ACCESS_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_API_VERSION=v18.0
COMPANY_WHATSAPP_PHONE=+919158019119
```

## Step 5: Test It

1. Restart Django server
2. Place a test order
3. Check console for: `[SUCCESS] WhatsApp sent via Meta Cloud API!`
4. Check recipient's WhatsApp

## Where to Find Credentials

### Phone Number ID:
- **Meta Business Suite** → **WhatsApp** → **API Setup**
- Or **Meta Developers** → **Your App** → **WhatsApp** → **API Setup**
- Look for **"Phone number ID"** or **"From"** field

### Access Token:
- **Meta Business Suite** → **WhatsApp** → **API Setup** → **Temporary Access Token**
- Or **Business Settings** → **System Users** → **Generate Token**

## Common Issues

**"Phone number ID not found"**
- Make sure your WhatsApp Business number is verified
- Check you're using the correct Phone Number ID (not the phone number itself)

**"Invalid access token"**
- Token may have expired (get a new one)
- For production, use System User token (doesn't expire)

**"403 Forbidden"**
- Check if System User has WhatsApp permissions
- Verify phone number is active and verified

## Your Current Setup

Based on your config, you already have:
- **Company WhatsApp**: `+919158019119`

You just need:
- **WHATSAPP_ACCESS_TOKEN** (from Meta)
- **WHATSAPP_PHONE_NUMBER_ID** (from Meta)

After setting these, your existing WhatsApp Business number will start sending notifications!

