# Django imports
from django.urls import path

# Local imports
from . import views


# ============================================================================
# URL PATTERNS - Organized by Functionality
# ============================================================================
# This file organizes all URL routes into clear sections:
# 1. Home & Page Views (home, about, FAQ, blog)
# 2. Order Management (order placement, status, success)
# 3. Payment Processing (Razorpay integration)
# 4. Legal & Policy Pages (required for e-commerce compliance)
# 5. Utility & System (SEO, admin tools, diagnostics)

urlpatterns = [
    # ========================================================================
    # HOME & PAGE VIEWS
    # ========================================================================
    # Main pages: home, about us, FAQ, blog
    path('', views.home, name='home'),  # Home page - serves at root for SEO
    path('home/', views.home_redirect, name='home_alt'),  # Redirect to root for SEO consolidation
    path('about-us/', views.about_us, name='about_us'),
    path('faq/', views.faq, name='faq'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<str:slug>/', views.blog_post, name='blog_post'),
    
    # ========================================================================
    # ORDER MANAGEMENT
    # ========================================================================
    # Order creation, processing, and status checking
    path('order/', views.place_order, name='place_order'),
    path('submit-order/', views.submit_order, name='submit_order'),
    path('order/success/', views.order_success, name='order_success'),
    path('check-status/<str:order_number>/', views.check_status, name='check_status'),
    path('get-order-history/', views.get_order_history, name='get_order_history'),
    
    # ========================================================================
    # PAYMENT PROCESSING
    # ========================================================================
    # Razorpay payment integration endpoints
    path('create-payment/', views.create_payment, name='create_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    
    # ========================================================================
    # LEGAL & POLICY PAGES
    # ========================================================================
    # Required legal pages for e-commerce compliance and Razorpay
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('return-policy/', views.return_policy, name='return_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('cancellations-and-refunds/', views.cancellations_and_refunds, name='cancellations_and_refunds'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('contact-us/', views.contact_us, name='contact_us'),
    
    # ========================================================================
    # UTILITY & SYSTEM
    # ========================================================================
    # SEO, admin tools, diagnostics, and system endpoints
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('healthz', views.healthz, name='healthz'),  # Health check for Render/uptime
    path('download-orders/', views.download_orders_excel, name='download_orders_excel'),
    path('test-razorpay/', views.test_razorpay, name='test_razorpay'),  # Diagnostic endpoint
    path('check-email-config/', views.check_email_config, name='check_email_config'),  # Diagnostic endpoint
]


