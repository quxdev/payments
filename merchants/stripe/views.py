import stripe
from django.conf import settings
from django.http.response import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from stripe.error import SignatureVerificationError
from django.shortcuts import render


def stripe_create_order(request, jsondata, action_url):
    jsondata.update({
        'action_url': action_url
    })
    return render(request, "merchants/stripe/home.html", jsondata)


class HomePageView(TemplateView):
    template_name = 'merchants/stripe/home.html'


class SuccessView(TemplateView):
    template_name = 'merchants/stripe/success.html'


class CancelledView(TemplateView):
    template_name = 'merchants/stripe/cancelled.html'


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        config = {
            'publicKey': settings.STRIPE_PUBLISHABLE_KEY
        }
        return JsonResponse(config, safe=False)


@csrf_exempt
def create_checkout_request(request):
    if request.method == 'GET':
        domain_url = settings.STRIPE_DOMAIN_URL
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection]
            #     - to display billing address details on the page
            # [customer]
            #     - if you have an existing Stripe Customer ID
            # [payment_intent_data]
            #     - capture the payment later
            # [customer_email]
            #     - prefill the email input in the form
            # For full details see
            # https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the
            # session ID set as a query param
            amount = request.GET.get('amount')
            currency = request.GET.get('currency')
            # receipt is cart slug/id
            receipt = request.GET.get('receipt')

            checkout_session = stripe.checkout.Session.create(
                client_reference_id=receipt,
                success_url=domain_url + 'payments/stripe/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'payments/stripe/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'name': 'Cart',
                        'quantity': 1,
                        'currency': currency,
                        'amount': amount,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful. session.completed")
        # TODO: run some custom code here
        print('payload checkout.session.completed =', payload)
        print('event checkout.session.completed =', event)

    return HttpResponse(status=200)
