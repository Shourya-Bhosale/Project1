# Step-by-Step Guide: Fix SendGrid Email

## Quick Overview
We'll create a new SendGrid API key and add it to Render. This will make email notifications work reliably.

---

## Step 1: Login to SendGrid

1. Go to: **https://app.sendgrid.com/**
2. Login with your account (or create one if needed)
3. Free tier allows **100 emails per day** (plenty for order notifications)

---

## Step 2: Create API Key

1. Once logged in, click on **Settings** (gear icon in left sidebar)
2. Click **API Keys** from the dropdown
3. Click the **Create API Key** button (top right, green button)

---

## Step 3: Configure API Key

1. **Name:** Enter `Django Shiv Dairy App`
2. **API Key Permissions:** Choose one of:
   - ✅ **Full Access** (easiest, recommended)
   - OR **Restricted Access** → Check only **Mail Send**
3. Click **Create & View** button

---

## Step 4: Copy the API Key ⚠️ IMPORTANT

1. A popup will show your API key
2. **Copy it immediately** - it starts with `SG.` followed by random characters
3. **Example format:** `SG.abcdefghijklmnopqrstuvwxyz123456789`
4. ⚠️ **You can only see this once!** Save it somewhere safe
5. Click **Done**

---

## Step 5: Update in Render

1. Go to **https://dashboard.render.com/**
2. Select your **Shiv Dairy website/service**
3. Click on **Environment** tab (left sidebar)
4. Find the variable: `SENDGRID_API_KEY`
5. Click on it (or add new if doesn't exist)
6. **Paste your new API key** in the Value field
7. Click **Save Changes**

---

## Step 6: Redeploy

1. After saving, Render will automatically redeploy
2. Wait 2-3 minutes for deployment to complete
3. You'll see a green checkmark when done

---

## Step 7: Test It

1. Go to your website
2. Place a **test order** (or use test mode)
3. Check your email: **shivorganicdairyfarms@gmail.com**
4. You should receive email with subject: **"New order #XXXX received - Shiv Organic Dairy Farm"**

---

## Verify It's Working

Check Render logs for:
```
✅ SendGrid email sent to shivorganicdairyfarms@gmail.com
```

If you see this, emails are working! 🎉

---

## Troubleshooting

### API Key Format
- Should start with `SG.`
- Should be around 70 characters long
- No spaces

### Still Getting 401 Error?
1. Double-check you copied the full key (no missing characters)
2. Make sure there are no extra spaces
3. Try creating a new API key with "Full Access"

### Not Receiving Emails?
1. Check spam folder
2. Check Render logs for errors
3. Verify email address: `shivorganicdairyfarms@gmail.com`

---

## Need Help?

If you encounter any issues at any step, let me know which step you're on and what error you see!

---

## Summary Checklist

- [ ] Logged into SendGrid
- [ ] Created new API Key (Full Access or Mail Send)
- [ ] Copied the API key (starts with SG.)
- [ ] Updated `SENDGRID_API_KEY` in Render
- [ ] Saved and redeployed
- [ ] Tested with a test order
- [ ] Received email confirmation

---

**Time Required:** ~5 minutes
**Difficulty:** Easy
**Result:** Reliable email notifications! 📧✅

