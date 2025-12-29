# Simple Email Setup - Using Brevo (Easiest Option)

## Why Brevo?
- ✅ **Very simple** API setup
- ✅ **300 emails/day FREE** (plenty for order notifications)
- ✅ Easy dashboard
- ✅ Simple integration
- ✅ Works great on Render

---

## Setup in 5 Minutes

### Step 1: Sign Up for Brevo (1 minute)

1. Go to: **https://www.brevo.com/signup/**
2. Create free account (or login if you have one)
3. Verify your email

### Step 2: Get API Key (1 minute)

1. After login, click your **profile icon** (top right)
2. Click **SMTP & API**
3. Click **API Keys** tab
4. Click **Generate a new API key**
5. Name it: `Shiv Dairy`
6. **Copy the key** (starts with `xkeysib-...`)
   - Example: `xkeysib-abc123def456ghi789jkl012mno345pqr678stu901vwx234`

### Step 3: Update Code (I'll do this for you)

I'll update the code to use Brevo instead of SendGrid - much simpler!

### Step 4: Add to Render (1 minute)

1. Go to: https://dashboard.render.com/
2. Your Service → **Environment**
3. **Remove** `SENDGRID_API_KEY` (or leave it empty)
4. **Add new variable:**
   - Key: `BREVO_API_KEY`
   - Value: `[paste your Brevo API key]`
5. Save

---

## That's It!

After redeploy, emails will work!

---

## Alternative: Even Simpler - Use Gmail with Better Config

If you want to stick with Gmail SMTP but make it work better, I can:
- Configure it to handle Render's restrictions better
- Add better error handling
- Make it more reliable

---

**Which do you prefer?**
1. **Brevo** (easiest, recommended) - I'll update code for you
2. **Gmail SMTP** - Try to make existing SMTP work better

Let me know and I'll handle the setup!

