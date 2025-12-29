# Email Not Working - Debug Steps

## Step 1: Check Render Logs

Go to Render Dashboard → Your Service → **Logs** tab

Look for lines after placing the order. What do you see?

**Good signs:**
- `📧 Sending email via Brevo to...`
- `✅ Brevo email sent to...`

**Bad signs:**
- `❌ Brevo error:`
- `⚠️ Brevo API key not configured`
- `Brevo returned status 401/403/400`
- No email logs at all

**Copy the log lines related to email and share them!**

---

## Common Issues & Fixes

### Issue 1: API Key Error
**If you see:** `401` or `Unauthorized`
**Fix:** API key might be wrong. Re-check it in Brevo dashboard.

### Issue 2: Key Not Configured
**If you see:** `Brevo API key not configured`
**Fix:** Make sure `BREVO_API_KEY` is saved in Render Environment.

### Issue 3: Brevo Account Not Verified
**If you see:** `403 Forbidden` or `Account not verified`
**Fix:** Verify your email in Brevo dashboard.

### Issue 4: No Logs
**If you see:** No email logs at all
**Fix:** Code might not be calling Brevo function. Check if order was saved.

---

## Quick Check

1. **In Render Environment**, verify:
   - `BREVO_API_KEY` exists
   - Value is: `606f529499a48ca0dcff66023f6490f5cfcceebed2f43d1f756e63cb3b837dce-KIK8fZQKQvDSMAK6`

2. **In Brevo Dashboard:**
   - Go to: https://app.brevo.com/
   - Check if your account is verified
   - Check API key status

---

**Please share what you see in Render logs after placing an order!**

