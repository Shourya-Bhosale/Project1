# How to Receive Order Notification Emails

## Current Email Configuration

**Company Email Address:** `shivorganicdairyfarms@gmail.com`

This email receives notifications for every new order.

## How to Change the Email Address

### Option 1: Set in Render (Production)

1. Go to your Render dashboard
2. Select your service
3. Go to **Environment** tab
4. Add/Update this variable:
   - **Key:** `ORDER_NOTIFICATION_EMAIL`
   - **Value:** `your-email@gmail.com` (your desired email)
5. Save and redeploy

### Option 2: Check Your Current Email

The emails should be going to: **shivorganicdairyfarms@gmail.com**

## How to Fix Email Delivery

Currently, emails are not being sent because SendGrid is failing. Here are your options:

### Option 1: Fix SendGrid (Recommended)

1. Go to https://app.sendgrid.com/
2. Login with your account
3. Navigate to: **Settings** → **API Keys**
4. Click **Create API Key**
5. Name it: "Django App"
6. Give it **Full Access** or **Restricted Access** → **Mail Send** permission
7. Copy the API key (you'll only see it once!)
8. In Render, update:
   - **Key:** `SENDGRID_API_KEY`
   - **Value:** [paste your new API key]
9. Redeploy

### Option 2: Use SMTP (Gmail)

Make sure these are set in Render:
- `EMAIL_HOST_USER` = `shivorganicdairyfarms@gmail.com`
- `EMAIL_HOST_PASSWORD` = [Gmail App Password]

**To get Gmail App Password:**
1. Go to your Google Account settings
2. Security → 2-Step Verification → App Passwords
3. Generate app password for "Mail"
4. Use that as `EMAIL_HOST_PASSWORD`

### Option 3: Check WhatsApp Instead (Already Working!)

Since WhatsApp notifications are working perfectly, you're already getting instant alerts at **+919158019119**. Email is just a backup.

## Testing Email

After fixing the configuration, place a test order and check:
- Your email inbox for: `shivorganicdairyfarms@gmail.com`
- Look for subject: "New order #XXXX received - Shiv Organic Dairy Farm"

## Multiple Email Addresses

If you want emails to go to multiple addresses, you can:
- Set up email forwarding in Gmail
- Or update the code to send to multiple recipients

## Summary

**Currently receiving:**
- ✅ WhatsApp at +919158019119 (WORKING)
- ❌ Email at shivorganicdairyfarms@gmail.com (NOT WORKING - SendGrid issue)

**To fix email:**
1. Fix SendGrid API key, OR
2. Use SMTP with Gmail App Password

**Quick check:** Check your Gmail inbox for `shivorganicdairyfarms@gmail.com` - emails should be there once SendGrid or SMTP is fixed.

