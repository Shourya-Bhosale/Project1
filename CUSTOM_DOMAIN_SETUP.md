# 🌐 Connect Your Custom Domain to Render

## Why It Still Shows "render.com" URL

Even though you bought `shivorganicdairyfarms.com`, you need to:
1. **Point your domain's DNS to Render** (at your domain registrar)
2. **Add the custom domain in Render dashboard**

---

## Step 1: Get Your Render Service URL

1. Go to: **https://dashboard.render.com/**
2. Click on your **Shiv Dairy service**
3. Note your Render URL (e.g., `shiv-dairy-website.onrender.com`)

---

## Step 2: Configure DNS at Your Domain Registrar

You need to add DNS records to point your domain to Render.

### Where to Add DNS Records:
- **Go to your domain registrar** (where you bought the domain)
  - Examples: GoDaddy, Namecheap, Google Domains, Cloudflare, etc.
- Find **DNS Management** or **DNS Settings**

### Add These DNS Records:

#### Option A: CNAME Record (Recommended - Easier)
```
Type: CNAME
Name: @ (or leave blank, or use "www")
Value: your-app-name.onrender.com
TTL: 3600 (or default)
```

**For both www and non-www:**
```
Type: CNAME
Name: www
Value: your-app-name.onrender.com
TTL: 3600

Type: CNAME
Name: @ (or blank)
Value: your-app-name.onrender.com
TTL: 3600
```

#### Option B: A Record (If CNAME doesn't work)
You'll need Render's IP addresses. Contact Render support or check their docs for current IPs.

**Note:** Some registrars don't allow CNAME on root domain (@). In that case:
- Use A records pointing to Render's IPs, OR
- Use www subdomain with CNAME

---

## Step 3: Add Custom Domain in Render

1. Go to: **https://dashboard.render.com/**
2. Click your **Shiv Dairy service**
3. Go to **Settings** tab
4. Scroll to **Custom Domains** section
5. Click **Add Custom Domain**
6. Enter: `shivorganicdairyfarms.com`
7. Click **Add**
8. Also add: `www.shivorganicdairyfarms.com` (repeat steps 5-7)

**Render will show you DNS instructions** - follow them!

---

## Step 4: Wait for DNS Propagation

- **DNS changes take 24-48 hours** to fully propagate
- Can be as fast as 5 minutes, but usually 1-2 hours
- You can check status at: https://www.whatsmydns.net/

---

## Step 5: SSL Certificate (Automatic)

Render automatically provisions SSL certificates for custom domains. This happens automatically after DNS is configured correctly.

---

## Troubleshooting

### Domain Still Shows Render URL?
1. ✅ Check DNS records are correct at your registrar
2. ✅ Check domain is added in Render dashboard
3. ✅ Wait 24-48 hours for DNS propagation
4. ✅ Clear browser cache
5. ✅ Try incognito/private browsing mode

### "Invalid Domain" Error in Render?
- Make sure DNS records are pointing to your Render service
- Wait for DNS to propagate (can take up to 48 hours)

### Domain Works But Shows "Not Secure"?
- SSL certificate is still provisioning (can take up to 24 hours)
- Wait for Render to automatically issue the certificate

---

## Quick Checklist

- [ ] Added CNAME/A records at domain registrar
- [ ] Added `shivorganicdairyfarms.com` in Render dashboard
- [ ] Added `www.shivorganicdairyfarms.com` in Render dashboard
- [ ] Waited for DNS propagation (24-48 hours)
- [ ] Tested domain in browser
- [ ] SSL certificate is active (check for padlock icon)

---

## Need Help?

**Common Domain Registrars:**
- **GoDaddy**: DNS Management → DNS Records
- **Namecheap**: Advanced DNS → Add New Record
- **Google Domains**: DNS → Custom Records
- **Cloudflare**: DNS → Add Record

**Render Support:**
- Check Render dashboard for specific DNS instructions
- Render shows exact DNS records needed when you add the domain

---

## Your Domain is Already Configured in Code! ✅

Your Django settings already include:
- `shivorganicdairyfarms.com`
- `www.shivorganicdairyfarms.com`

So once DNS and Render are configured, it will work immediately!

