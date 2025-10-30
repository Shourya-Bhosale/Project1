# 🚀 Quick SendGrid Fix - 3 Steps

## The Fastest Way to Get Emails Working

### 1️⃣ Get API Key
- Go to: https://app.sendgrid.com/
- Settings → API Keys → **Create API Key**
- Name: `Shiv Dairy`
- Permissions: **Full Access**
- **Copy the key** (starts with `SG.`)

### 2️⃣ Add to Render
- Go to: https://dashboard.render.com/
- Your Service → **Environment**
- Find `SENDGRID_API_KEY`
- Paste the key → **Save**

### 3️⃣ Test
- Render will auto-redeploy (2 minutes)
- Place a test order
- Check email: **shivorganicdairyfarms@gmail.com**

---

**That's it!** ✨

If you see `✅ SendGrid email sent` in logs, it's working!

---

## Common Mistakes to Avoid
- ❌ Copying only part of the key (must be complete)
- ❌ Adding spaces or extra characters
- ❌ Using old expired key
- ❌ Not waiting for redeploy to finish

---

## Need the Detailed Steps?
See: `SENDGRID_SETUP_STEPS.md`

