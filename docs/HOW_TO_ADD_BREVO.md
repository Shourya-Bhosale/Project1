# How to Add Brevo API Key

## For Production (Render) - Add as Environment Variable ✅

Since your website is hosted on Render, add it there:

### Steps:
1. Go to: **https://dashboard.render.com/**
2. Click your **Shiv Dairy service**
3. Click **Environment** tab (left sidebar)
4. Click **Add Environment Variable** or find existing `BREVO_API_KEY`
5. Set:
   - **Key:** `BREVO_API_KEY`
   - **Value:** `YOUR_BREVO_API_KEY`
6. Click **Save Changes**

**Render will automatically redeploy (wait 2 minutes)**

---

## For Local Development - Use .env File (Optional)

If you're testing locally on your computer, you can also create a `.env` file:

1. Create `.env` file in root directory
2. Add:
   ```
   BREVO_API_KEY=YOUR_BREVO_API_KEY
   ```

**But for your live website, use Render Environment Variables!**

---

## Summary

- **Production (Live website):** Add in Render Dashboard → Environment ✅
- **Local testing:** Can use `.env` file (optional)

**Start with Render Dashboard - that's what matters for your live site!**

