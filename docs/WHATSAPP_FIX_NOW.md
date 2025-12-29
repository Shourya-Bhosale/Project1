# 🚨 WhatsApp Not Working - Quick Fix

## Most Likely Issues

### Issue 1: Not Configured in Render
The `COMPANY_WHATSAPP_PHONE` might not be set in Render.

**Fix:**
1. Go to Render Dashboard
2. Your Service → Environment
3. Add/Check: `COMPANY_WHATSAPP_PHONE` = `+919158019119`
4. Save and wait 2 minutes for redeploy

### Issue 2: Not Enrolled in Twilio Sandbox ⚠️ MOST COMMON

If using Twilio Sandbox, **you MUST enroll first**:

1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Find the **join keyword** (looks like "pizza", "hello", etc.)
3. From WhatsApp on phone **+919158019119**, send this message:
   ```
   join [keyword]
   ```
   To this number: **+1 415 523 8886**
4. You'll get a confirmation when enrolled

**Then try placing an order again.**

---

## Check What's Wrong

After placing a test order, check Render logs and tell me what you see:

**Good:**
```
✅ Company WhatsApp notification sent successfully!
```

**Bad - Not enrolled:**
```
❌ All WhatsApp methods failed:
   - Error 21608: not enrolled
   → Send 'join [keyword]' to +1 415 523 8886
```

**Bad - Not configured:**
```
ℹ️ Company WhatsApp not configured (set COMPANY_WHATSAPP_PHONE)
```

---

## Quick Check in Render

Go to Render → Environment and verify these exist:

✅ `COMPANY_WHATSAPP_PHONE` = `+919158019119`
✅ `TWILIO_ACCOUNT_SID` = `ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
✅ `TWILIO_AUTH_TOKEN` = `your_twilio_auth_token`

---

## Next Steps

1. **Check Render Environment** - Make sure `COMPANY_WHATSAPP_PHONE` is set
2. **Enroll in Sandbox** - Send "join [keyword]" from +919158019119
3. **Test** - Place a test order
4. **Check Logs** - See what error appears (if any)

**Tell me:**
- What do you see in Render logs after placing an order?
- Is `COMPANY_WHATSAPP_PHONE` set in Render Environment?

