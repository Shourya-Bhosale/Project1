# Fix Email Notifications - Step by Step

## Goal
Get order notification emails working at: **shivorganicdairyfarms@gmail.com**

## Current Status
- ❌ SendGrid API key is invalid (401 error)
- ✅ SMTP fallback is configured (but unreliable on Render)

## Solution: Fix SendGrid API Key

### Step 1: Get New SendGrid API Key (3 minutes)

1. **Open:** https://app.sendgrid.com/
2. **Login** (or create free account if needed)
3. Click **Settings** (gear icon, left sidebar)
4. Click **API Keys**
5. Click **Create API Key** (green button, top right)

**Configure the key:**
- **Name:** `Shiv Dairy App`
- **Permissions:** Choose **Full Access** (easiest)
- Click **Create & View**

**IMPORTANT: Copy the key NOW!** (starts with `SG.`)
- Example: `SG.abcdefghijklmnopqrstuvwxyz1234567890`
- You can only see it once!

### Step 2: Add to Render (2 minutes)

1. **Open:** https://dashboard.render.com/
2. Click your **Shiv Dairy service**
3. Click **Environment** tab (left sidebar)
4. Find: `SENDGRID_API_KEY`
5. **Paste your new key** (replace the old one)
6. Click **Save Changes**

### Step 3: Wait & Test (2 minutes)

1. Render will auto-redeploy (wait 2-3 minutes)
2. Place a **test order** on your website
3. Check email: **shivorganicdairyfarms@gmail.com**
4. Look for subject: **"New order #XXXX received - Shiv Organic Dairy Farm"**

---

## Verify It's Working

After placing a test order, check **Render Logs** for:

**Success:**
```
✅ SendGrid email sent to shivorganicdairyfarms@gmail.com
```

**Still failing:**
```
❌ SendGrid error: HTTP Error 401: Unauthorized
```

---

## Troubleshooting

### Still Getting 401 Error?
- Make sure you copied the **entire** API key (no missing characters)
- No extra spaces before/after the key
- Try creating a new API key with **Full Access**

### Not Receiving Emails?
1. Check **spam folder**
2. Check Render logs for errors
3. Verify email address: `shivorganicdairyfarms@gmail.com`

### Want Different Email Address?
In Render Environment, add:
- `ORDER_NOTIFICATION_EMAIL` = `your-email@gmail.com`

---

## Quick Checklist

- [ ] Logged into SendGrid
- [ ] Created new API key (Full Access)
- [ ] Copied the key (starts with SG.)
- [ ] Updated `SENDGRID_API_KEY` in Render
- [ ] Saved and redeployed
- [ ] Tested with test order
- [ ] Received email ✅

---

**Start now:**
1. Go to: https://app.sendgrid.com/
2. Follow Step 1 above
3. Then do Step 2 in Render
4. Test and confirm!

Let me know if you get stuck at any step!

