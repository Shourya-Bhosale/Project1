# WhatsApp Not Working - Fix Guide

## Problem
You're not receiving WhatsApp messages at +919158019119 when orders are placed.

## Quick Diagnosis

### Check 1: Is it configured in Render?
In Render Dashboard → Environment, check:
- `COMPANY_WHATSAPP_PHONE` = `+919158019119`
- `TWILIO_ACCOUNT_SID` = `ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
- `TWILIO_AUTH_TOKEN` = `your_twilio_auth_token`

### Check 2: Twilio Sandbox Enrollment
If using Twilio Sandbox, **the phone number must be enrolled first**:

1. Get your Twilio Sandbox keyword:
   - Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
   - Find the join keyword (e.g., "pizza", "hello", etc.)

2. Send enrollment message:
   - Send a WhatsApp message to: **+1 415 523 8886**
   - Message: `join [your-keyword]`
   - Example: `join pizza`

3. You'll receive confirmation when enrolled

### Check 3: Number Format
The number must be in international format:
- ✅ Correct: `+919158019119`
- ❌ Wrong: `919158019119` (missing +)
- ❌ Wrong: `9158019119` (missing country code)

---

## Step-by-Step Fix

### Step 1: Verify Render Configuration

1. Go to **Render Dashboard** → Your Service → **Environment**
2. Check these variables exist and are correct:
   ```
   COMPANY_WHATSAPP_PHONE = +919158019119
   TWILIO_ACCOUNT_SID = ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   TWILIO_AUTH_TOKEN = your_twilio_auth_token
   ```
3. If missing, **add them** and **save**
4. Wait for redeploy (2 minutes)

### Step 2: Enroll in Twilio Sandbox

If using Twilio Sandbox (default):

1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Find the join keyword (shown on the page)
3. From WhatsApp on +919158019119, send:
   ```
   join [keyword]
   ```
   to: **+1 415 523 8886**
4. Wait for confirmation message

### Step 3: Test

1. Place a test order on your website
2. Check Render logs for:
   - `✅ Company WhatsApp notification sent successfully!` = Working
   - `⚠️ Company WhatsApp failed` = Still not working
   - `ℹ️ Company WhatsApp not configured` = Not set in Render

---

## Common Issues

### Issue 1: "Not configured" Error
**Problem:** `COMPANY_WHATSAPP_PHONE` not set in Render
**Fix:** Add it in Render Environment variables

### Issue 2: "21608 - Not enrolled"
**Problem:** Phone number not enrolled in Twilio Sandbox
**Fix:** Send "join [keyword]" to +1 415 523 8886

### Issue 3: Messages sent but not received
**Possible causes:**
- Wrong phone number format
- Number not enrolled
- WhatsApp not installed on that number

**Check Render logs to see what error appears**

### Issue 4: Production vs Sandbox
If you want to send to ANY number (not just enrolled):
- Need to upgrade Twilio to production WhatsApp
- Contact Twilio support
- Currently only sandbox works (enrolled numbers only)

---

## Quick Test

Run this to check configuration:

```python
python test_company_whatsapp.py
```

Should show:
```
Company WhatsApp Phone: +919158019119
Twilio Configuration:
  Account SID: ✅ Set
  Auth Token: ✅ Set
✅ Configuration Complete!
```

---

## Verify in Render Logs

After placing an order, check logs for:

**If working:**
```
📱 Attempting WhatsApp to company +919158019119...
✅ Company WhatsApp notification sent successfully!
```

**If failing:**
```
📱 Attempting WhatsApp to company +919158019119...
❌ All WhatsApp methods failed:
   - Error: [error message]
```

**If not configured:**
```
ℹ️ Company WhatsApp not configured (set COMPANY_WHATSAPP_PHONE)
```

---

## Need Help?

Tell me what you see in Render logs after placing a test order, and I can help diagnose the exact issue!

