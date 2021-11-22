import datetime

import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from customer.payment.swipez.views.views import swipez_payment
from customer.payment.swipez.views.views import swipez_payment_payload
from customer.payment.swipez.views.views import swipez_webhook_payload


class HomePageView(TemplateView):
    template_name = 'merchants/swipez/example/pay.html'


def test(request):
    data = swipez_payment_payload(testpayload())
    return render(request, 'merchants/swipez/example/test.html', data)


def payment(request):
    # get all data
    postdata = {f: request.POST.get(f, None) for f in request.POST}

    # Example - so fix callback to request host
    baseurl = request.scheme + "://" + request.get_host()
    if postdata['return_url'] and not postdata['return_url'].startswith('http'):
        postdata['return_url'] = baseurl + postdata['return_url']

    # generate payload
    payload = swipez_payment_payload(postdata)

    return swipez_payment(payload)


@csrf_exempt
def response(request):
    # Success
    # status = 'success' | message = 'Transaction Successful'
    # Canceled
    # status = 'failed'  | message = 'Cancelled by user'

    data = swipez_webhook_payload(request.POST)
    return render(request, 'merchants/swipez/example/response.html', data)


def testpayload():
    return {
        'account_id': 'M000000041',
        'return_url': '/payments/swipez/example/webhook/',
        'reference_no': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        'description': 'Swipez Test Payment',
        'amount': '101.00',
        'name': 'Mohan Singh',
        'address': '2000 Senapati Bapat Marg',
        'city': 'Pune',
        'state': 'MH',
        'postal_code': '411008',
        'phone': '02067331397',
        'email': 'mohansingh@notgmail.com',
    }


def test_payment():
    postdata = testpayload()
    data = swipez_payment_payload(postdata)

    r = requests.post(data['url'], data['payload'])
    data.update({'response': r})

    return data
