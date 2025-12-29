# 🚨 URGENT: Domain Not Working - Quick Fix Guide

## The Problem
You can't access your website at `shivorganicdairyfarms.com`

## Quick Diagnosis Steps

### Step 1: Check What Error You See

**What happens when you visit `https://shivorganicdairyfarms.com`?**

- ❌ **"This site can't be reached"** → DNS issue
- ❌ **"404 Not Found"** → Domain not added in Render
- ❌ **"DisallowedHost" error** → ALLOWED_HOSTS issue
- ❌ **SSL Certificate error** → SSL not issued yet
- ❌ **Blank page / Nothing loads** → Deployment issue

**Tell me which error you see!**

---

## Most Common Fixes

### Fix 1: Check Domain is Added in Render

1. **Go to:** https://dashboard.render.com/
2. **Click your service** (Shiv Dairy)
3. **Go to Settings** → **Custom Domains**
4. **Check if `shivorganicdairyfarms.com` is listed:**
   - ✅ **If listed:** Check status (should have green checkmarks)
   - ❌ **If NOT listed:** Add it (see below)

**To add domain:**
1. Click **"Add Custom Domain"**
2. Enter: `shivorganicdairyfarms.com`
3. Click **Add**
4. Render will show DNS instructions

---

### Fix 2: Check DNS Configuration

**The domain must point to Render via DNS records.**

1. **Go to your domain registrar** (where you bought the domain)
   - Examples: GoDaddy, Namecheap, Google Domains, Cloudflare
2. **Find DNS Management / DNS Settings**
3. **Check if CNAME record exists:**
   - **Type:** CNAME
   - **Name:** @ (or blank)
   - **Value:** `shiv-dairy-website.onrender.com` (or your Render URL)
4. **If missing or wrong:** Add/update the CNAME record

**To check DNS:**
- Go to: https://dnschecker.org/
- Enter: `shivorganicdairyfarms.com`
- Check if CNAME points to your Render URL

---

### Fix 3: Check Render Subdomain Status

**If you disabled Render Subdomain, that's fine - but check:**

1. **Render Dashboard** → **Settings** → **Render Subdomain**
2. **If toggle is OFF:**
   - ✅ This is correct for custom domain only
   - ✅ Your domain should still work
   - ❌ If it doesn't work, DNS might be wrong

**If toggle is ON:**
- Both Render URL and custom domain should work
- If custom domain doesn't work, it's a DNS issue

---

### Fix 4: Check SSL Certificate

1. **Render Dashboard** → **Settings** → **Custom Domains**
2. **Click on `shivorganicdairyfarms.com`**
3. **Check SSL status:**
   - ✅ **"Certificate Issued"** → Good
   - ⚠️ **"Pending"** → Wait 10-15 minutes
   - ❌ **"Error"** → DNS not pointing correctly

**If SSL is pending:**
- Wait 10-15 minutes after DNS is correct
- Render issues SSL automatically

---

### Fix 5: Check Deployment Status

1. **Render Dashboard** → **Your Service**
2. **Check status:**
   - ✅ **"Live"** (green) → Good
   - ⚠️ **"Building"** → Wait for deployment
   - ❌ **"Failed"** → Check logs

3. **Check Logs:**
   - Click **Logs** tab
   - Look for errors
   - Check if application started successfully

---

### Fix 6: Test Render URL

**Try accessing via Render URL:**
- `https://shiv-dairy-website.onrender.com`

**If Render URL works but custom domain doesn't:**
- ✅ Application is fine
- ❌ DNS or domain configuration issue

**If Render URL also doesn't work:**
- ❌ Application/deployment issue
- Check Render logs for errors

---

## Emergency Fix: Re-enable Render Subdomain

**If you need the site working immediately:**

1. **Render Dashboard** → **Settings** → **Render Subdomain**
2. **Turn toggle ON** (if it's off)
3. **Wait 2-3 minutes**
4. **Test:** `https://shiv-dairy-website.onrender.com` should work
5. **Then fix DNS** for custom domain

**This gets your site working while you fix DNS.**

---

## Step-by-Step Recovery

### If Domain Was Removed from Render:

1. **Add it back:**
   - Render Dashboard → Settings → Custom Domains
   - Click "Add Custom Domain"
   - Enter: `shivorganicdairyfarms.com`
   - Follow DNS instructions

2. **Update DNS at registrar:**
   - Use the exact DNS records Render shows
   - Wait 24-48 hours for propagation

### If DNS is Wrong:

1. **Get correct DNS records:**
   - Render Dashboard → Settings → Custom Domains
   - Click on your domain
   - Copy the exact DNS records shown

2. **Update at domain registrar:**
   - Go to your registrar's DNS management
   - Update/Add the CNAME record
   - Use exact values from Render

3. **Wait 24-48 hours** for DNS propagation

### If ALLOWED_HOSTS Issue:

**The code already includes your domain, but check:**

1. **Render Dashboard** → **Environment**
2. **Check if `ALLOWED_HOSTS` is set:**
   - If set, make sure it includes: `shivorganicdairyfarms.com`
   - If not set, that's fine (code has defaults)

---

## Quick Test Checklist

- [ ] Domain added in Render Dashboard?
- [ ] DNS records pointing to Render?
- [ ] SSL certificate issued?
- [ ] Service is "Live" in Render?
- [ ] Render URL works?
- [ ] Checked Render logs for errors?

---

## What to Tell Me

**Please share:**
1. **What error you see** when visiting the domain
2. **Is domain listed** in Render → Settings → Custom Domains?
3. **What's the SSL status** in Render?
4. **Does Render URL work?** (`shiv-dairy-website.onrender.com`)
5. **What's the service status?** (Live/Building/Failed)

**This will help me give you the exact fix!**

---

## Most Likely Issue

**Based on what we did:**
- If you disabled Render Subdomain → That's fine, custom domain should still work
- **Most likely:** DNS not pointing correctly, or domain removed from Render

**Quick fix:** Re-enable Render Subdomain temporarily to get site working, then fix DNS.


