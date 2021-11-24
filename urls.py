from django.urls import path
from django.urls import re_path

from .views import *
from .merchants.views import *

app_name = 'customer'

urlpatterns = [
    path('', PaymentHome.as_view(), name='home'),

    path('product/<str:productsku>/payment/', getitem, name='buyitem'),
    path('cart/<str:slug>/payment/', getpaid, name='payment'),
    path('payment/webhook/<str:reference>/', webhook, name='webhook'),

    path('address/', AddressListView.as_view(), name='address_home'),
    path('address/new/', AddressCreateView.as_view(), name='address_new'),
    path('address/<int:pk>/edit/', AddressUpdateView.as_view(), name='address_edit'),

    path('customer/', CustomerListView.as_view(), name='customer_home'),
    path('customer/new/', CustomerCreateView.as_view(), name='customer_new'),
    path('customer/<str:slug>/edit/', CustomerUpdateView.as_view(), name='customer_edit'),

    path('invoice/', InvoiceListView.as_view(), name='invoice_home'),
    path('invoice/new/', InvoiceCreateView.as_view(), name='invoice_new'),
    path('invoice/<str:slug>/edit/', InvoiceUpdateView.as_view(), name='invoice_edit'),
    path('invoice/<str:slug>/', InvoiceDetailView.as_view(), name='invoice_detail'),

    path('cart/', CartListView.as_view(), name='cart_home'),
    path('cart/new/', CartCreateView.as_view(), name='cart_new'),
    re_path('cart/(?:(?P<pk>[0-9]+)/)?', CartItemPage.as_view(), name='cart_edit'),

    # for customer
    re_path('checkout/(?:(?P<pk>[0-9]+)/)?', CartItemPage.as_view(), name='cart_checkout'),
    re_path('kyc/(?:(?P<userid>[0-9]+)/)?', KYCView.as_view(), name='account_kyc'),

    path('payment/', PaymentListView.as_view(), name='payment_home'),
    path('payment/new/', PaymentCreateView.as_view(), name='payment_new'),
    path('payment/<str:slug>/edit/', PaymentUpdateView.as_view(), name='payment_edit'),
    path('payment/<str:slug>/', PaymentDetailView.as_view(), name='payment_detail'),


    path('invoice-by-customer/<int:customer_id>/',
         getinvoice_by_customer, name='invoice_by_customer'),
    path('open-cart-by-customer/<int:customer_id>/',
         getopen_cart_by_customer, name='open_cart_by_customer'),
    path('address-by-user/<int:user_id>/',
         getaddress_by_user, name='address_by_user'),
    path('product-by-id/<int:product_id>/',
         getproduct_by_id, name='product_by_id'),
    path('cart-validation/<int:ivrid>/',
         cart_validation, name='cart_validation'),
    path('customer-autocomplete/', getcustomers, name='customer-autocomplete'),

    path('user-autocomplete', UserAutocomplete.as_view(), name='user-autocomplete'),

]
