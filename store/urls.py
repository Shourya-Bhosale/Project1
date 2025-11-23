from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),  # Serve home at root - best for SEO
    path('home/', views.home, name='home_alt'),  # Keep as alias for backwards compatibility
    path('healthz', views.healthz, name='healthz'),
    path('order/', views.place_order, name='place_order'),
    path('submit-order/', views.submit_order, name='submit_order'),
    path('check-status/<str:order_number>/', views.check_status, name='check_status'),
    path('order/success/', views.order_success, name='order_success'),
    # Razorpay payment URLs
    path('create-payment/', views.create_payment, name='create_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    path('test-razorpay/', views.test_razorpay, name='test_razorpay'),
    path('check-email-config/', views.check_email_config, name='check_email_config'),
    path('get-order-history/', views.get_order_history, name='get_order_history'),
    # Legal pages for Razorpay compliance
    path('return-policy/', views.return_policy, name='return_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('cancellations-and-refunds/', views.cancellations_and_refunds, name='cancellations_and_refunds'),
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]


