#!/usr/bin/env python
"""
Test order confirmation email function directly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shivdairy.settings')
django.setup()

from store.models import Order
from store.views import _send_order_emails

print("=" * 60)
print("Testing Order Confirmation Email Function")
print("=" * 60)

# Get the most recent order
try:
    order = Order.objects.order_by('-id').first()
    if order:
        print(f"Found order: #{order.order_number}")
        print(f"Customer: {order.customer_name}")
        print(f"Email: {order.email}")
        print(f"Payment Method: {order.payment_method}")
        print()
        print("Calling _send_order_emails function...")
        _send_order_emails(order)
        print("[DONE] Email function completed")
        print()
        print("Check console above for any [ERROR] or [WARNING] messages")
        print("If you see [SUCCESS] messages, emails were sent")
    else:
        print("No orders found in database")
        print("Place a test order first, then run this script again")
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

