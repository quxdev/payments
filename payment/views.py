from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .razorpay.views import razorpay_create_order
from .razorpay.views import razorpay_verify_signature
from .swipez.views import swipez_payment
from .swipez.views import swipez_payment_payload
from .swipez.views import swipez_webhook_payload
from ..models import *


@login_required
def getitem(request, productsku: str):
    user = request.user
    if user.is_anonymous:
        return

    # invoice = Invoice.create(request.user)
    # invoice.additem(productsku)
    product = Product.objects.get_or_none(sku=productsku)
    if product is None or product.is_active is False:
        raise Http404('Product not exists')

    # Customer create
    customer_obj = Customer.objects.get_or_none(primary_contact=user)
    if customer_obj is None:
        customer_obj, created = Customer.objects.get_or_create(
            primary_contact=user
        )
        if created:
            customer_obj.email = user.email
            customer_obj.phone = user.profile.phone
            customer_obj.contact_name = user.profile.get_fullname()
            customer_obj.users.add(user)
            customer_obj.save()

    # invoice_obj = Invoice.create(customer_obj, product, ivr)
    # return getpaid(request, invoice_obj.slug)
    cart_obj = Cart.get_cart_object(customer_obj)
    if cart_obj:
        cart_obj.create_item(product)
        cart_obj.reset_items()
    else:
        cart_obj = Cart.create(customer_obj, product)

    return HttpResponseRedirect(reverse("customer:cart_edit", kwargs={'pk': cart_obj.id}))


def send_email_on_payment_visit(cart):
    # subject = "New Payment visit cart: " + str(cart.slug)

    # message = cart.to_text()

    # json_data = {
    #     'targets': settings.TEAM_SALES,
    #     'subject': subject,
    #     'message': message,
    #     'sender': 'no-reply@blacklab.app',
    # }

    # create_async_task('core.comm.tasks.send_async_email', json_data)

    pass


# @login_required
def getpaid(request, slug: str):
    # if request.user.is_anonymous:
    #     return

    # invoice = Invoice.objects.get_or_none(slug=invoice_slug)
    cart = Cart.objects.get_or_none(slug=slug)

    # if invoice.unpaid() == 0:
    #     raise Http404('There is no pending payments. Thank you')
    if not cart:
        raise Http404('Invalid URL')
    if cart.is_open is False:
        raise Http404('Cart is already closed. Thank you')
    if cart.customer.gstin in ['', None] and cart.customer.pan in ['', None]:
        next_page = '?next='+reverse('customer:payment', kwargs={'slug': slug})
        if request.user.is_staff or request.user.is_superuser:
            url = reverse(
                'account_kyc',
                kwargs={'userid': cart.customer.primary_contact_id}
            )
            return HttpResponseRedirect(url+next_page)

        return HttpResponseRedirect(reverse('account_kyc')+next_page)

    send_email_on_payment_visit(cart)

    if settings.PAYMENT_PROVIDER == 'Swipez':
        rawdata = cart.swipez_payload()
        baseurl = request.scheme + "://" + request.get_host()
        rawdata['return_url'] = baseurl + rawdata['return_url']
        payload = swipez_payment_payload(rawdata)

        return swipez_payment(payload)

    elif settings.PAYMENT_PROVIDER == 'RazorPay':
        rawdata = cart.razorpay_payload()
        action_url = reverse('customer:webhook', kwargs={'reference': rawdata['receipt']})
        return razorpay_create_order(request, rawdata, action_url)


@csrf_exempt
def webhook(request, reference: str):
    data = {
        'invoice': None,
        'payment': None,
        'reference': reference,
        'error': None
    }

    post_dict = request.POST.dict()
    print('post_dict =', post_dict)

    # payment = Payment.objects.get_or_none(reference=reference)
    # payment = Payment.objects.filter(invoice__invoice_number=reference).last()

    # invoice = Invoice.objects.get_or_none(invoice_number=reference)
    # if invoice is None:
    #     data['error'] = 'PaymentNotFound'
    #     return render(request, 'failure.html', data)

    cart = Cart.objects.get_or_none(slug=reference)
    if cart is None:
        data['error'] = 'PaymentNotFound'
        return render(request, 'failure.html', data)

    invoice = Invoice.create(cart)

    payment = Payment.create(invoice)
    if payment is None:
        data['error'] = 'PaymentNotFound'
        return render(request, 'failure.html', data)

    data['slug'] = payment.invoice.slug
    if payment.is_processed:
        data['payment'] = model_to_dict(payment, exclude=['id', 'post_dict', 'new_object_id'])
        data['invoice'] = model_to_dict(payment.invoice)
        data['error'] = 'InvoiceIsPaid'
        return render(request, 'failure.html', data)

    if settings.PAYMENT_PROVIDER == 'Swipez':
        payload = swipez_webhook_payload(request.POST)
        postdata = payload['data']
        if payload['signature'] != postdata['checksum']:
            data['error'] = 'ChecksumFailed'
            send_email_for_payment(payment)
            return render(request, 'failure.html', data)

        if request.POST.get('status', 'failed') == 'success':
            payment.is_processed = True
            payment.payment_date = timezone.now().today()
            payment.paid_amount = Decimal(request.POST.get('amount', 0))
        payment.source_reference = request.POST.get('reference_no', None)
        payment.post_dict.update(post_dict)
        payment.save()

        # [payment.swipez_setattr(f, postdata[f]) for f in postdata]

        if postdata.get('status', 'failed') == 'failed':
            data['error'] = 'PaymentFailed'
            data['message'] = postdata.get('message', None)

        data['payment'] = model_to_dict(payment, exclude=['id', 'post_dict', 'new_object_id'])
        data['invoice'] = model_to_dict(payment.invoice)

        # return render(request, 'failure.html', data)
        send_email_for_payment(payment)
        return HttpResponseRedirect(reverse('customer:invoice_detail', kwargs={'slug': invoice.slug}))

    elif settings.PAYMENT_PROVIDER == 'RazorPay':
        # https://razorpay.com/docs/payment-gateway/quick-integration/#step-3-store-the-fields-in-your-database
        # only for successful payments
        razorpay_payment_id = post_dict.get('razorpay_payment_id', None)
        # used to verify the payment.
        razorpay_signature = post_dict.get('razorpay_signature', None)
        razorpay_order_id = post_dict.get('razorpay_order_id', None)
        if razorpay_payment_id:
            payment.source_reference = razorpay_payment_id
        # payment.post_dict = post_dict
        payment.post_dict.update(post_dict)
        payment.save()

        is_paid = razorpay_verify_signature(
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        )
        print('is_paid =', is_paid)
        if is_paid:
            payment.is_processed = True
            payment.payment_date = timezone.now().today()
            # payment.paid_amount = Decimal(request.POST.get('amount', 0))
            payment.save()
        else:
            data['error'] = 'ChecksumFailed'

        data['payment'] = model_to_dict(payment, exclude=['id', 'post_dict', 'new_object_id'])
        data['invoice'] = model_to_dict(payment.invoice)

        # return render(request, 'failure.html', data)
        send_email_for_payment(payment)
        return HttpResponseRedirect(reverse('customer:invoice_detail', kwargs={'slug': invoice.slug}))
