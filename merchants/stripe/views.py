import stripe
from django.conf import settings
from django.http.response import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from stripe.error import SignatureVerificationError


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
        domain_url = 'http://localhost:8080/'
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
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'payments/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'payments/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'name': 'Personal',
                        'quantity': 1,
                        'currency': 'inr',
                        'amount': '50000',
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

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event and event['type'] == 'checkout.session.completed':
        # TODO: run some custom code here
        print("Payment was successful.")

    return HttpResponse(status=200)
