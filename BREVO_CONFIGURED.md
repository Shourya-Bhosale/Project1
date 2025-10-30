# Brevo Configuration - Ready to Add to Render

## Your Brevo Credentials

**API Key (Recommended - Simplest):**
```
YOUR_BREVO_API_KEY
```

**SMTP Details (Alternative):**
- Server: smtp-relay.brevo.com
- Port: 587
- Login: 9a3ca1001@smtp-brevo.com
- Password: [same as API key]

---

## Add to Render NOW

### Option 1: Use API (Recommended - Already Implemented)

1. Go to: https://dashboard.render.com/
2. Your Service → Environment
3. Add/Update:
   - **Key:** `BREVO_API_KEY`
   - **Value:** `YOUR_BREVO_API_KEY`
4. Save

**That's it!** The code is already configured to use this.

### Option 2: Use SMTP (Alternative)

If you prefer SMTP instead, I can update the code to use:
- Host: smtp-relay.brevo.com
- Port: 587
- Username: 9a3ca1001@smtp-brevo.com
- Password: [your API key]

---

## After Adding to Render

1. Wait 2 minutes for redeploy
2. Place a test order
3. Check email: shivorganicdairyfarms@gmail.com
4. You should receive the email! ✅

---

## Quick Checklist

- [ ] Go to Render Dashboard
- [ ] Add `BREVO_API_KEY` = `YOUR_BREVO_API_KEY`
- [ ] Save
- [ ] Wait for redeploy
- [ ] Test with order
- [ ] Check email! 📧

**The API method is already coded and ready - just add the key to Render!**

