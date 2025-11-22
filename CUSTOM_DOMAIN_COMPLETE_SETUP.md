# 🌐 COMPLETE GUIDE: Show Your Domain (shivorganicdairyfarms.com) Instead of "Render Application"

## The Problem
Your website shows "Render application" instead of your custom domain `shivorganicdairyfarms.com`.

## Root Cause
The custom domain is not properly connected to Render. This requires **DNS configuration** at your domain registrar.

---

## ✅ PERMANENT FIX - Follow These Steps

### STEP 1: Get Your Render Service URL

1. Go to: **https://dashboard.render.com/**
2. Click on your **Shiv Dairy service** (or whatever it's named)
3. Look at the top - you'll see your Render URL
   - Example: `shiv-dairy-website.onrender.com`
   - Or: `shiv-dairy-dbweb.onrender.com`
4. **Write this down** - you'll need it for DNS

---

### STEP 2: Add Custom Domain in Render Dashboard

1. In Render Dashboard → Your Service
2. Go to **Settings** tab (left sidebar)
3. Scroll to **Custom Domains** section
4. Click **"Add Custom Domain"** button
5. Enter: `shivorganicdairyfarms.com`
6. Click **Add**
7. **Render will show you DNS instructions** - follow them exactly!

8. **Also add www version:**
   - Click **"Add Custom Domain"** again
   - Enter: `www.shivorganicdairyfarms.com`
   - Click **Add**

**Important:** Render will show you specific DNS records to add. **Use those exact values**, not generic ones.

---

### STEP 3: Configure DNS at Your Domain Registrar

**Where is your domain registered?**
- GoDaddy
- Namecheap
- Google Domains
- Cloudflare
- Other?

#### Find Your Domain Registrar:
1. Go to: **https://whois.net/**
2. Enter: `shivorganicdairyfarms.com`
3. Look for **"Registrar"** - that's where you manage DNS

---

### STEP 4: Add DNS Records (At Your Domain Registrar)

**Go to your domain registrar's DNS management page**

#### Option A: Use Render's Instructions (RECOMMENDED)

1. In Render Dashboard → Settings → Custom Domains
2. Click on `shivorganicdairyfarms.com`
3. Render shows **exact DNS records** to add
4. **Copy those exact values**
5. Add them at your domain registrar

#### Option B: Generic CNAME Setup (If Render doesn't show specific records)

**At your domain registrar, add these DNS records:**

**For root domain (shivorganicdairyfarms.com):**
```
Type: CNAME
Name: @ (or leave blank, or "apex")
Value: YOUR-RENDER-URL.onrender.com
TTL: 3600 (or default)
```

**For www (www.shivorganicdairyfarms.com):**
```
Type: CNAME
Name: www
Value: YOUR-RENDER-URL.onrender.com
TTL: 3600 (or default)
```

**Replace `YOUR-RENDER-URL.onrender.com` with your actual Render URL from Step 1**

---

### STEP 5: Wait for DNS Propagation

- **DNS changes take 24-48 hours** to fully propagate
- Some changes appear in 1-2 hours
- **Don't panic if it doesn't work immediately**

**Check DNS propagation:**
- Go to: **https://dnschecker.org/**
- Enter: `shivorganicdairyfarms.com`
- Select **CNAME** record type
- Check if it shows your Render URL

---

### STEP 6: Verify SSL Certificate

1. After DNS propagates, Render **automatically issues SSL certificate**
2. Check in Render Dashboard → Settings → Custom Domains
3. Look for **green checkmark** or **"SSL Active"**
4. This usually takes 5-10 minutes after DNS is correct

---

### STEP 7: Test Your Domain

1. **Wait 24-48 hours after DNS changes**
2. Visit: `https://shivorganicdairyfarms.com`
3. Should show your website (not "Render application")
4. Visit: `https://www.shivorganicdairyfarms.com`
5. Should also work

**If still showing "Render application":**
- Clear browser cache (Ctrl+Shift+Delete)
- Try incognito/private window
- Check DNS propagation status
- Verify DNS records are correct

---

## 🔍 TROUBLESHOOTING

### Still seeing "Render application"?

#### Check 1: DNS Records
- Go to: **https://dnschecker.org/**
- Enter your domain
- Check if CNAME points to your Render URL
- If not, DNS hasn't propagated yet (wait 24-48 hours)

#### Check 2: Render Custom Domain Status
- Render Dashboard → Settings → Custom Domains
- Is domain listed?
- Is there a green checkmark?
- Any error messages?

#### Check 3: SSL Certificate
- Render Dashboard → Settings → Custom Domains
- Is SSL certificate active?
- If not, wait 10-15 minutes after DNS is correct

#### Check 4: Browser Cache
- Clear browser cache completely
- Try different browser
- Try incognito mode

---

## 📋 CHECKLIST

- [ ] Got Render service URL from dashboard
- [ ] Added `shivorganicdairyfarms.com` in Render → Settings → Custom Domains
- [ ] Added `www.shivorganicdairyfarms.com` in Render → Settings → Custom Domains
- [ ] Found domain registrar (whois.net)
- [ ] Added CNAME records at domain registrar
- [ ] Waited 24-48 hours for DNS propagation
- [ ] Verified DNS propagation (dnschecker.org)
- [ ] SSL certificate active in Render
- [ ] Tested domain in browser
- [ ] Website shows correctly (not "Render application")

---

## 🆘 STILL NOT WORKING?

### Common Issues:

1. **"Invalid Domain" in Render**
   - DNS records not pointing to Render
   - Wait for DNS propagation
   - Double-check DNS records are correct

2. **SSL Certificate Pending**
   - DNS must be correct first
   - Wait 10-15 minutes after DNS is correct
   - Render issues SSL automatically

3. **Domain Shows "Render Application"**
   - DNS not propagated yet (wait 24-48 hours)
   - Wrong DNS records
   - Domain not added in Render dashboard

4. **Browser Shows Old Page**
   - Clear browser cache
   - Try incognito mode
   - DNS might not be propagated yet

---

## ✅ WHAT TO EXPECT

**After proper setup:**
- ✅ `https://shivorganicdairyfarms.com` → Shows your website
- ✅ `https://www.shivorganicdairyfarms.com` → Shows your website
- ✅ SSL certificate active (padlock icon)
- ✅ No "Render application" message
- ✅ Your custom domain in browser address bar

---

## 📞 NEED HELP?

**Share these details:**
1. Your Render service URL
2. Your domain registrar name
3. Screenshot of DNS records at registrar
4. Screenshot of Render → Settings → Custom Domains
5. What you see when visiting your domain

**This will help diagnose the exact issue!**

---

## ⚡ QUICK SUMMARY

1. **Add domain in Render** → Settings → Custom Domains
2. **Add DNS records** at your domain registrar (CNAME to Render URL)
3. **Wait 24-48 hours** for DNS propagation
4. **SSL certificate** issues automatically
5. **Test your domain** - should work!

**The key is DNS configuration at your domain registrar. Render can't do this for you - you must do it at where you bought the domain.**

