from django.urls import path
from . import views


urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
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
    # Legal pages for Razorpay compliance
    path('return-policy/', views.return_policy, name='return_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
]


