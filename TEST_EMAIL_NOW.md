# Test Email Now - After Deployment

## Step 1: Place a Test Order

1. Go to your website: **https://shivorganicdairyfarms.com** (or your Render URL)
2. **Place a test order**
   - Add products to cart
   - Fill in order form
   - Submit the order

## Step 2: Check for Success

### Check Render Logs:
1. Go to Render Dashboard
2. Your Service → **Logs** tab
3. Look for:
   - ✅ `Brevo email sent to shivorganicdairyfarms@gmail.com` = **SUCCESS!**
   - ❌ `Brevo error` = Need to check what's wrong

### Check Your Email:
1. Open: **shivorganicdairyfarms@gmail.com**
2. Look for subject: **"New order #XXXX received - Shiv Organic Dairy Farm"**
3. Check spam folder if not in inbox

---

## What Should Happen:
1. Order gets saved ✅
2. WhatsApp notification sent (if enrolled) ✅
3. **Email sent via Brevo** ✅ (What we're testing!)

---

## If It Works:
You'll see in logs:
```
✅ Brevo email sent to shivorganicdairyfarms@gmail.com
```

And receive email with order details!

---

## If It Doesn't Work:
Check logs and tell me what error you see. Common issues:
- API key still wrong
- Brevo account needs verification
- Network issue

**Go ahead and place a test order now!** 🚀

