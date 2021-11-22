from django.urls import path

from .views import *

app_name = 'razorpay'

urlpatterns = [
    path('payment/', razorpay_payment, name="payment"),
    path('success/', razorpay_payment_success, name="payment-success"),
]
