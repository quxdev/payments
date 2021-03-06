# QUX Payments

> Note: This project will work only after `qux` exist in the project.

# Setup
Get Project from Git
```sh
git clone https://github.com/quxdev/payments.git
```

Add these configuration in `project/project/settings.py` file after adding `payments` app in your project
```sh
import os
import dotenv

dotenv.load_dotenv(os.path.join(BASE_DIR, 'project/.env'))

INSTALLED_APPS += [
    'django.contrib.sites',

    'qux',
    'qux.seo',
    'payments',

    'rangefilter',
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
    ('css', os.path.join(BASE_DIR, "qux/static/css")),
    # payments/common/js is for Cart and Stripe payment
    ('js', os.path.join(BASE_DIR, "payments/common/js")),
]

SITE_ID = 1
TEAM_SALES = ['emailid_id@example.com']
SERVICE_TEAM = ['emailid_id@example.com']
PRODUCT_GST_PERCENT = 18
# 'RazorPay' OR 'Swipez' or 'Stripe'
PAYMENT_PROVIDER = 'Stripe'
KYC_GST_PAN_REQUIRED = True
CART_INVOICE_ITEM_CUSTOM_FIELD = True
SHIPPING_ADDRESS_REQUIRED = True
ON_PAYMENT_SUCCESS = 'payments.models.OnPaymentSuccess'
LOGO_PATH = 'logo/razorpay_4x1.svg'

PAYMENT_EMAIL_ON_NEW_CUSTOMER = True
PAYMENT_EMAIL_ON_NEW_PAYMENT = True
PAYMENT_EMAIL_ON_PAYMENT_VISIT = True

# RazorPay
RAZORPAY_KEY = os.getenv('RAZORPAY_KEY', None)
RAZORPAY_SECRET = os.getenv('RAZORPAY_SECRET', None)

# Stripe
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', None)
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', None)
STRIPE_ENDPOINT_SECRET = os.getenv('STRIPE_ENDPOINT_SECRET', None)

# Swipez
SWIPEZ_SECRET_KEY = os.getenv('SWIPEZ_SECRET_KEY', None)
SWIPEZ_MODE = os.getenv('SWIPEZ_MODE', 'TEST')

PAYMENT_CURRENCY = 'USD';

INVOICE_SELLER = {
    'name': 'Name',
    'address': 'A-01, Address, City, India',
    'gstin': '22ABCDE1703R1YZ'
}
```

Create `project/project/.env` file and store these required variables
```sh
export RAZORPAY_KEY="for-razorpay-payment-gateway"
export RAZORPAY_SECRET="for-razorpay-payment-gateway"

export SWIPEZ_SECRET_KEY="for-swipez-payment-gateway"

export STRIPE_PUBLISHABLE_KEY="for-stripe-payment-gateway"
export STRIPE_SECRET_KEY="for-stripe-payment-gateway"
export STRIPE_ENDPOINT_SECRET="for-stripe-payment-gateway"
```

# Add URL in the project
Add payments url in `project/project/urls.py` file
```sh
from django.urls import path
from django.urls import include
urlpatterns += [
    path('billing/', include('payments.urls')),
]
```

# Optional : to override base class/method/url
Override urls before payments url in `project/project/urls.py` file
```sh
urlpatterns += [
    # change checkout url before defining package urls. ex."payments" package
    path('billing/invoice/<str:slug>/', CustomInvoiceDetailView.as_view(), name='invoice_detail'),
    path('billing/product/<str:productsku>/payment/', custom_getitem, name='buyitem'),
    re_path('billing/kyc/(?:(?P<userid>[0-9]+)/)?', CustomKYCView.as_view(), name='account_kyc'),
    re_path('billing/cart/(?:(?P<pk>[0-9]+)/)?', CustomCartItemPage.as_view(), name='cart_edit'),
    path('billing/', include('payments.urls')),
]
```

# Note for stripe configuration
Ref - https://testdriven.io/blog/django-stripe-tutorial/
```sh
# Use `Test mode` On/Off button for test and production environment
# For Production server, url : https://dashboard.stripe.com/apikeys
STRIPE_PUBLISHABLE_KEY="Publishable key"
STRIPE_SECRET_KEY="Secret key"
# from webhook url detail click on `Signing secret`
STRIPE_ENDPOINT_SECRET="Signing secret from webhook detail page"


# For Dev server use test account, url : https://dashboard.stripe.com/test/apikeys
STRIPE_PUBLISHABLE_KEY="Publishable key"
STRIPE_SECRET_KEY="Secret key"
# from webhook url detail click on `Signing secret`
STRIPE_ENDPOINT_SECRET="Signing secret from webhook detail page"


# For Local server use test account, url : https://dashboard.stripe.com/test/apikeys
STRIPE_PUBLISHABLE_KEY="Publishable key"
STRIPE_SECRET_KEY="Secret key"
# for localhost: Download "Stripe CLI" from https://stripe.com/docs/stripe-cli#install url
# On login you will get secret endpoint key which you need to add in below variable
STRIPE_ENDPOINT_SECRET="Signing secret from webhook detail page"
# use below command in terminal at stripe package path to test localhost payment checkout
# while testing you need to `disable` test webhook urls from https://dashboard.stripe.com/test/webhooks
./stripe listen --forward-to localhost:8000/billing/stripe/webhook/
```
