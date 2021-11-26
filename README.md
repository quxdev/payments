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
    ('css', os.path.join(BASE_DIR, "qux/static/css"))
]

SITE_ID = 1
TEAM_SALES = ['emailid_id@example.com']
SERVICE_TEAM = ['emailid_id@example.com']
PRODUCT_GST_PERCENT = 18
# 'RazorPay' OR 'Swipez'
PAYMENT_PROVIDER = 'RazorPay'
KYC_GST_PAN_REQUIRED = True
ON_PAYMENT_SUCCESS = 'payments.models.OnPaymentSuccess'

SWIPEZ_SECRET_KEY = os.getenv('SWIPEZ_SECRET_KEY', None)
SWIPEZ_MODE = os.getenv('SWIPEZ_MODE', 'TEST')

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
