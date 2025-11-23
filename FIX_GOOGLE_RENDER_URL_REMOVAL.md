# 🔧 Fix "URL not in property" Error - Remove Render URL from Google

## The Error You're Seeing

**"URL not in property"** when trying to remove:
- `https://shiv-dairy-website.onrender.com/*`

## Why This Happens

The Render URL (`shiv-dairy-website.onrender.com`) is **NOT** in your `shivorganicdairyfarms.com` property in Google Search Console. It's either:
- In a different property (if you added it separately)
- Not verified in Search Console at all
- Google just found it automatically

**This is actually GOOD news** - it means Google Search Console is correctly set up for your custom domain only!

---

## ✅ CORRECT SOLUTION - Don't Try to Remove Render URL

**Instead, do this:**

### Step 1: Disable Render Subdomain (MOST IMPORTANT)

**This prevents Google from finding the Render URL:**

1. **Go to:** https://dashboard.render.com/
2. **Click your service** (Shiv Dairy)
3. **Go to Settings** → **Render Subdomain**
4. **Turn toggle OFF:**
   - Click the toggle
   - Type: `sudo subdomain web service shiv-dairy-website`
   - Click "Disable Render Subdomain"

**Why this works:**
- When Render subdomain is disabled, the Render URL stops working
- Google can't access it anymore
- Google will automatically stop showing it in search results
- No need to manually remove it!

---

### Step 2: Request Indexing of Your Custom Domain

**Force Google to use YOUR domain:**

1. **Go to:** https://search.google.com/search-console/
2. **Select property:** `shivorganicdairyfarms.com` ✅
3. **Go to:** **URL Inspection**
4. **Enter:** `https://shivorganicdairyfarms.com/home/`
5. **Click:** **Test Live URL**
6. **Wait** for test (30-60 seconds)
7. **Click:** **Request Indexing**

**Repeat for:**
- `https://shivorganicdairyfarms.com/`
- `https://shivorganicdairyfarms.com/order/`

---

### Step 3: Submit/Update Sitemap

**Make sure Google knows about your custom domain:**

1. **Google Search Console** → **Sitemaps**
2. **Check if sitemap exists:**
   - If old one exists → **Remove it**
3. **Add new sitemap:**
   - Enter: `https://shivorganicdairyfarms.com/sitemap.xml`
   - Click **Submit**
4. **Verify:**
   - All URLs should use `shivorganicdairyfarms.com`
   - NOT `shiv-dairy-website.onrender.com`

---

### Step 4: Set Preferred Domain

**Tell Google which domain to use:**

1. **Google Search Console** → **Settings** (gear icon, bottom left)
2. **Click:** **Domain Settings**
3. **Select:** `shivorganicdairyfarms.com` (without www)
4. **Click:** **Save**

**This tells Google:** "Always use this domain, ignore any other URLs"

---

### Step 5: Wait and Monitor

**Timeline:**
- **24-48 hours:** Google re-crawls your custom domain
- **48-72 hours:** Render URL stops appearing in search
- **1-2 weeks:** "Render application" completely disappears

**Check progress:**
- Search: `site:shivorganicdairyfarms.com`
- Should show your pages
- Should NOT show Render URL

---

## Alternative: If You Want to Remove Render URL Manually

**If Render URL is in a different property:**

1. **Check if you have another property:**
   - Google Search Console → Property selector (top)
   - Look for: `shiv-dairy-website.onrender.com`
   - If it exists, select it

2. **If property exists:**
   - Go to **Removals**
   - Request removal of all URLs
   - Then delete the property

3. **If property doesn't exist:**
   - Don't worry about it
   - Just disable Render subdomain (Step 1)
   - Google will stop indexing it automatically

---

## Why This Approach Works Better

**Instead of trying to remove the Render URL:**
- ✅ **Disable Render subdomain** → URL stops working → Google can't access it
- ✅ **Request indexing of custom domain** → Google uses your domain
- ✅ **Set preferred domain** → Google knows which one to use
- ✅ **Submit sitemap** → Google discovers all your pages on custom domain

**Result:**
- Google stops showing Render URL (because it doesn't work)
- Google shows your custom domain (because you requested it)
- No manual removal needed!

---

## Summary

**Don't try to remove Render URL manually** - you'll get "URL not in property" error.

**Instead:**
1. ✅ **Disable Render Subdomain** (stops Render URL from working)
2. ✅ **Request indexing** of your custom domain
3. ✅ **Submit sitemap** with custom domain URLs
4. ✅ **Set preferred domain** in Search Console
5. ✅ **Wait 24-48 hours** for Google to update

**After 48 hours, Google will show your custom domain, not "Render application"!**


