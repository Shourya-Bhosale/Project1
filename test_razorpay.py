#!/usr/bin/env python
"""
Test Razorpay integration
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shivdairy.settings')
django.setup()

import razorpay
from django.conf import settings

def test_razorpay_connection():
    """Test Razorpay API connection"""
    try:
        # Set test keys (you'll need to replace with your actual keys)
        key_id = "rzp_live_RVik0FVKDm160O"  # Your live key
        key_secret = "YOUR_SECRET_KEY"  # You need to provide this
        
        print(f"Testing Razorpay with Key ID: {key_id}")
        
        # Initialize client
        client = razorpay.Client(auth=(key_id, key_secret))
        
        # Test API connection by fetching account details
        try:
            account = client.account.fetch()
            print("✅ Razorpay connection successful!")
            print(f"Account Name: {account.get('name', 'N/A')}")
            print(f"Account Email: {account.get('email', 'N/A')}")
            return True
        except Exception as e:
            print(f"❌ Razorpay API error: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Razorpay setup error: {str(e)}")
        return False

def test_payment_order_creation():
    """Test creating a payment order"""
    try:
        key_id = "rzp_live_RVik0FVKDm160O"
        key_secret = "YOUR_SECRET_KEY"  # You need to provide this
        
        client = razorpay.Client(auth=(key_id, key_secret))
        
        # Create a test order
        order_data = {
            'amount': 10000,  # ₹100 in paise
            'currency': 'INR',
            'receipt': 'test_order_001',
            'notes': {
                'test': 'true'
            }
        }
        
        order = client.order.create(data=order_data)
        print("✅ Test order created successfully!")
        print(f"Order ID: {order['id']}")
        print(f"Amount: ₹{order['amount']/100}")
        print(f"Currency: {order['currency']}")
        return True
        
    except Exception as e:
        print(f"❌ Order creation failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Razorpay Integration")
    print("=" * 50)
    
    print("\n1. Testing Razorpay Connection...")
    connection_ok = test_razorpay_connection()
    
    if connection_ok:
        print("\n2. Testing Order Creation...")
        test_payment_order_creation()
    
    print("\n" + "=" * 50)
    print("Test completed!")
