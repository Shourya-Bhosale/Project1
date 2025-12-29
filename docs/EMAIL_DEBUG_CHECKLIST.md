# Email Debug Checklist

## Current Status:
- ✅ Test email works (`python test_email.py`)
- ❌ Order confirmation emails not received
- ✅ SMTP backend configured correctly
- ✅ Email function is called

## Diagnostic Steps:

### Step 1: Check if Email Function is Being Called
**Do this:** Place a COD order and watch Django console output

**Look for:**
```
[ORDER] COD order placed: #ORDER_NUMBER, Customer: email@example.com
[EMAIL] Starting email notification for order #ORDER_NUMBER
[EMAIL] Customer email: email@example.com
[EMAIL] Notification thread started for order #ORDER_NUMBER
```

**If these messages appear:**
→ Function IS being called → Go to Step 2

**If these messages DON'T appear:**
→ Function NOT being called → Bug in order flow

---

### Step 2: Check if Emails Actually Send
**After Step 1, look for:**
```
[SUCCESS] SMTP email sent to customer: email@example.com
[SUCCESS] Company SMTP email sent
```

**If these appear:**
→ Emails ARE being sent → Check spam folder, email provider blocking

**If you see [WARNING] or [ERROR]:**
→ Email sending failing → Check error message for cause

---

### Step 3: Test Email Function Directly
**Run this script after placing an order:**
```bash
python test_order_email.py
```

This will test the email function with your most recent order.

**If this works:**
→ Email function is fine → Issue is in order flow timing

**If this fails:**
→ Email function has a bug → Check error message

---

### Step 4: Check Common Issues

#### Issue A: Thread Completing Before Email Sends
**Symptom:** Emails not sent even though function is called
**Check:** Console shows thread started but no [SUCCESS] messages
**Fix:** Already changed to non-daemon thread (should be fixed)

#### Issue B: Gmail Blocking "From" Address
**Symptom:** Emails sent but bounce or go to spam
**Check:** Email `from_email` must match Gmail account
**Current:** `shivorganicdairyfarms@gmail.com` ✅

#### Issue C: Background Thread Error
**Symptom:** Function called but thread crashes silently
**Check:** Look for `[ERROR] Exception in notification thread` in logs
**Fix:** All emojis removed (should be fixed)

---

## Quick Test Commands:

### Test 1: Manual Email Function Test
```bash
python test_order_email.py
```

### Test 2: SMTP Configuration Test
```bash
python test_email.py
```

### Test 3: Check Recent Orders
```bash
python manage.py shell
>>> from store.models import Order
>>> Order.objects.order_by('-id')[:3]
```

---

## What to Check Next:
1. **Place a test COD order**
2. **Watch Django console** for the log messages above
3. **Run `python test_order_email.py`** to test with real order data
4. **Check spam folder** in both customer and company email
5. **Share console output** if emails still don't work

