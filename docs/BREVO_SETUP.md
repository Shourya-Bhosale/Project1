# 🎯 Brevo Email Setup - SUPER SIMPLE!

## Why Brevo?
- ✅ **3 minutes setup** (vs SendGrid's complexity)
- ✅ **300 emails/day FREE** (more than enough!)
- ✅ Simple API - no complex configuration
- ✅ Works perfectly on Render

---

## Setup Steps (3 Minutes Total)

### Step 1: Get Brevo API Key (2 minutes)

1. **Go to:** https://www.brevo.com/signup/
   - Create free account (or login if you have one)
   - Verify your email

2. **Get API Key:**
   - Login to Brevo
   - Click your **profile icon** (top right)
   - Click **SMTP & API**
   - Click **API Keys** tab
   - Click **Generate a new API key**
   - Name: `Shiv Dairy`
   - **Copy the key** (starts with `xkeysib-...`)
     - Example: `xkeysib-abc123def456ghi789jkl012mno345pqr678`

### Step 2: Add to Render (1 minute)

1. Go to: **https://dashboard.render.com/**
2. Your Service → **Environment** tab
3. Click **Add Environment Variable**
4. **Key:** `BREVO_API_KEY`
5. **Value:** Paste your Brevo API key
6. Click **Save**

**That's it!** Render will auto-redeploy (2 minutes)

---

## Test It

1. Place a test order on your website
2. Check email: **shivorganicdairyfarms@gmail.com**
3. You should receive: **"New order #XXXX received - Shiv Organic Dairy Farm"**

---

## Check if Working

In Render logs, you'll see:
```
✅ Brevo email sent to shivorganicdairyfarms@gmail.com
```

---

## That's All!

No complex setup, no extra steps. Just:
1. Sign up → Get API key → Paste in Render → Done! ✨

**Much simpler than SendGrid!**

