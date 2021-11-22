import hashlib

from django.conf import settings

# Shared fields
# reference_no = reference_no
# name = billing_name
# address = billing_address
# city = billing_city
# state = billing_state
# postal_code = billing_postal_code
# phone = billing_mobile
# email = billing_email

swipez_request_fields = [
    'account_id', 'return_url', 'reference_no', 'amount', 'description',
    'name', 'address', 'city', 'state', 'postal_code', 'phone', 'email',
]
swipez_response_fields = [
    'transaction_id', 'bank_ref_no', 'reference_no', 'mode', 'amount',
    'status', 'date', 'message', 'merchant_email', 'company_name',
    'billing_name', 'billing_email', 'billing_mobile', 'billing_address',
    'billing_city', 'billing_state', 'billing_postal_code', 'checksum'
]
swipez_optional_fields = [
    'udf1', 'udf2', 'udf3', 'udf4', 'udf5'
]


def get_url():
    mode = settings.SWIPEZ_MODE
    mode = mode.upper() if mode else 'TEST'

    return {
        'PROD': 'https://www.swipez.in/xway/secure',
        'TEST': 'https://h7sak8am43.swipez.in/xway/secure'
    }[mode]


def get_request_signature(data):
    if settings.SWIPEZ_SECRET_KEY is None:
        return

    print(settings.SWIPEZ_SECRET_KEY)
    try:
        sig_data = settings.SWIPEZ_SECRET_KEY + \
            "|" + data['account_id'] + \
            "|" + data['amount'] + \
            "|" + data['reference_no'] + \
            "|" + data['return_url']
        print(sig_data)
        sig_hash = hashlib.md5(sig_data.encode())
        signature = sig_hash.hexdigest()
    except TypeError:
        print("get_request_signature()[53]")
        print(data)
        signature = None

    return signature


def get_response_signature(data):
    if settings.SWIPEZ_SECRET_KEY is None:
        return

    try:
        sig_data = settings.SWIPEZ_SECRET_KEY + \
            "|" + data['amount'] + \
            "|" + data['reference_no'] + \
            "|" + data['billing_email']
        sig_hash = hashlib.md5(sig_data.encode())
        signature = sig_hash.hexdigest()
    except TypeError:
        print(data)
        signature = None

    return signature
