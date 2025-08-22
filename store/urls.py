from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('order/', views.place_order, name='place_order'),
    path('submit-order/', views.submit_order, name='submit_order'),
    path('check-status/<str:order_number>/', views.check_status, name='check_status'),
    path('order/success/', views.order_success, name='order_success'),
]


