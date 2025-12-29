# Why SMTP Gmail Isn't Working - Troubleshooting Guide

## The Main Problem

**SMTP on Render is very difficult** because:
1. **Port blocking**: Render blocks outbound SMTP ports (25, 587, 465) for security
2. **Network restrictions**: Even if ports are open, Gmail may block connections from cloud IPs
3. **SendGrid is preferred**: This is why SendGrid (API-based) is recommended for Render

## Why Your SMTP Isn't Working

### Issue 1: Render Blocking SMTP Ports
Render blocks SMTP ports by default. Even with correct credentials, SMTP connections fail.

### Issue 2: Gmail App Password Not Set in Render
Check in Render Dashboard → Environment:
- Is `EMAIL_HOST_PASSWORD` set?
- Is it a valid Gmail App Password (16 characters, no spaces)?

### Issue 3: SendGrid Present But Failing
When `SENDGRID_API_KEY` exists (even if invalid), Django tries SendGrid first, and SMTP fallback may not trigger properly.

## Solutions

### ✅ Solution 1: Fix SendGrid (BEST OPTION)

**Why it's better:**
- Works on Render without port issues
- No network restrictions
- More reliable

**Steps:**
1. Go to https://app.sendgrid.com/
2. Settings → API Keys → Create API Key
3. Choose "Restricted Access" → Select "Mail Send"
4. Copy the key
5. In Render: Update `SENDGRID_API_KEY`
6. Redeploy

### Solution 2: Remove SendGrid Key (Force SMTP)

If you REALLY want SMTP:
1. In Render: **Delete** the `SENDGRID_API_KEY` variable (or set to empty)
2. Set these in Render:
   - `EMAIL_HOST_USER` = `shivorganicdairyfarms@gmail.com`
   - `EMAIL_HOST_PASSWORD` = `[your 16-char Gmail App Password]`
3. **Important**: SMTP may still fail due to Render network restrictions

**How to get Gmail App Password:**
1. Google Account → Security
2. Enable 2-Step Verification (if not enabled)
3. Click "App Passwords"
4. Generate password for "Mail"
5. Copy the 16-character password (no spaces)

### Solution 3: Use WhatsApp Only (Already Working!)

Since WhatsApp notifications are working perfectly, you can:
- ✅ Continue using WhatsApp for instant alerts
- ✅ Fix SendGrid later when convenient
- ✅ Check Django Admin for orders if needed

## Testing

After fixing, place a test order and check Render logs for:

**If SendGrid works:**
```
✅ SendGrid email sent to shivorganicdairyfarms@gmail.com
```

**If SMTP works:**
```
✅ Company SMTP email sent (backup to WhatsApp)
```

**If both fail:**
```
⚠️ Company notification failed (both WhatsApp and email)
```

## Recommendation

**Best path forward:**
1. Fix SendGrid API key (5 minutes, most reliable)
2. Keep WhatsApp (already working)
3. Ignore SMTP for now (not reliable on Render)

## Quick Check

To see what's configured in Render:
1. Go to Render Dashboard → Your Service → Environment
2. Check these variables:
   - `SENDGRID_API_KEY` - Should be valid or empty
   - `EMAIL_HOST_USER` - Should be `shivorganicdairyfarms@gmail.com`
   - `EMAIL_HOST_PASSWORD` - Should be Gmail App Password (16 chars)

If `SENDGRID_API_KEY` exists but is invalid, that's why SMTP isn't being tried properly.

