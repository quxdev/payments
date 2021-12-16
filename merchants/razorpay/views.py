import os
import razorpay
import hmac
import hashlib

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

# https://dev.to/po/razozpay-integration-with-django-1b9i


def razorpay_get_client():
    return razorpay.Client(auth=(os.getenv('RAZORPAY_KEY'), os.getenv('RAZORPAY_SECRET')))


def razorpay_create_order(request, jsondata, action_url):
    client = razorpay_get_client()
    print('jsondata =', jsondata)
    response = client.order.create(jsondata)
    print(response)

    context = {
        'response': response,
        'key': os.getenv('RAZORPAY_KEY'),
        'action_url': action_url,
        'logo_path': settings.LOGO_PATH
    }
    return render(request, "merchants/razorpay/razorpay_payment.html", context)


def razorpay_verify_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    # client = razorpay_get_client()
    # params_dict = {
    #     # "razorpay_order_id": payment.post_dict['create_order']['order_id'],
    #     "razorpay_order_id": razorpay_order_id,
    #     # 'razorpay_order_id': payment.invoice.invoice_number,
    #     "razorpay_payment_id": razorpay_payment_id,
    #     "razorpay_signature": razorpay_signature
    # }
    # status = client.utility.verify_payment_signature(**params_dict)
    # print(f'razorpay_verify_signature status = {status}, {params_dict}')
    # return status

    message = razorpay_order_id + "|" + razorpay_payment_id

    signature = hmac.new(
        bytes(os.getenv('RAZORPAY_SECRET'), 'latin-1'),
        msg=bytes(message, 'latin-1'), digestmod=hashlib.sha256
    ).hexdigest()

    if razorpay_signature == signature:
        return True
    else:
        return False


def razorpay_payment(request):
    amount = 100  # 100 here means 1 dollar,1 rupree if currency INR
    jsondata = {'amount': amount, 'currency': settings.PAYMENT_CURRENCY, 'receipt': 'invoice003'}
    action_url = reverse('razorpay:payment-success')
    return razorpay_create_order(request, jsondata, action_url)


@csrf_exempt
def razorpay_payment_success(request):
    if request.method == "POST":
        print(request.POST)
        return HttpResponse("Done payment hurrey!")
