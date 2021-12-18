import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from ..swipez import *


def swipez_payment(data):
    """

    :param data: {'url': URL, 'payload': {}}
    :return:
    """
    # payment.1e9solutions.com
    # webhook should be to the machine making the request
    # or do we make all payments through a separate machine
    # without user access

    session = requests.session()
    session.headers.update({'referer': 'qux.dev'})
    r = session.post(data['url'], data['payload'])
    print(r.content)
    return HttpResponse(r.content)


def swipez_payment_payload(postdata):
    fields = swipez_request_fields + swipez_optional_fields
    data = {f: postdata.get(f, None) for f in fields if f in postdata}

    data['secure_hash'] = get_request_signature(data)

    return {
        'url': get_url(),
        'payload': data
    }


@csrf_exempt
def swipez_webhook(request):
    # Success
    # status = 'success' | message = 'Transaction Successful'
    # Canceled
    # status = 'failed'  | message = 'Cancelled by user'

    data = swipez_webhook_payload(request.POST)
    print(data)
    return render(request, 'response.html', data)


def swipez_webhook_payload(data):
    fields = swipez_response_fields + swipez_optional_fields
    data = {f: data.get(f, None) for f in fields}
    signature = get_response_signature(data)

    return {
        'data': data,
        'signature': signature
    }
