# Brevo API Key Issue - Render Not Accepting xkeysib-

## Try Without the Prefix

If Render rejects `xkeysib-`, try using just the key part:

**Use this in Render:**
```
606f529499a48ca0dcff66023f6490f5cfcceebed2f43d1f756e63cb3b837dce-KIK8fZQKQvDSMAK6
```

The code should work either way - with or without the prefix.

---

## Alternative: Check Your Brevo Dashboard

1. Go to: https://app.brevo.com/
2. Profile → SMTP & API → API Keys
3. Check if your key shows with or without `xkeysib-` prefix
4. Copy exactly what's shown there

---

## Test It

After saving:
1. Wait 2 minutes for redeploy
2. Place a test order
3. Check Render logs for:
   - `✅ Brevo email sent` = Working!
   - `❌ Brevo error` = Still needs fixing

The code will try the key as-is, so it should work with just the key value!

