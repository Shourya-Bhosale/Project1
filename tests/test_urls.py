#!/usr/bin/env python
"""
Test URL patterns
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shivdairy.settings')
django.setup()

from django.urls import reverse
from store.urls import urlpatterns

def test_urls():
    """Test URL patterns"""
    print("Testing URL patterns...")
    print(f"Number of URL patterns: {len(urlpatterns)}")
    
    for pattern in urlpatterns:
        print(f"Pattern: {pattern.pattern} -> {pattern.name}")
    
    # Test specific URLs
    try:
        order_url = reverse('place_order')
        print(f"✅ Order URL: {order_url}")
    except Exception as e:
        print(f"❌ Order URL error: {e}")
    
    try:
        home_url = reverse('home')
        print(f"✅ Home URL: {home_url}")
    except Exception as e:
        print(f"❌ Home URL error: {e}")

if __name__ == "__main__":
    test_urls()
