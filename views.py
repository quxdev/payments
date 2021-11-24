import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from rest_framework import permissions
from rest_framework.views import APIView

from .forms import *
from qux.seo.mixin import SEOMixin
from .models import *


class PaymentHome(LoginRequiredMixin, SEOMixin, TemplateView):
    template_name = 'home.html'
    extra_context = {
        'breadcrumbs': ['Home']
    }


class AddressListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Address
    queryset = Address.objects.all()
    template_name = 'address/address_list.html'
    fields = ['name', ]
    extra_context = {
        'breadcrumbs': ['Address'],
    }
    permission_required = ('core.view_address', )

    def get_queryset(self):
        queryset = Address.objects.all().order_by('-id')

        user = self.request.user
        if not user.is_staff and not user.is_superuser:
            queryset = queryset.filter(
                user=user
            )

        return queryset


class AddressCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Address
    form_class = AddressForm
    template_name = 'address/address_form.html'
    permission_required = ('core.add_address', )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create Address.'
        context['submit_btn_text'] = 'Create'
        return context

    def get_success_url(self, *args, **kwargs):
        return reverse('customer:address_home')


class AddressUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'address/address_form.html'
    permission_required = ('core.change_address', )

    def get_success_url(self, *args, **kwargs):
        return reverse('customer:address_home')


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'customer/customer_detail.html'

    def get_object(self):
        user = self.request.user
        if not user.is_staff and not user.is_superuser:
            customer = Customer.objects.get_or_none(
                primary_contact=user
            )
        else:
            if 'pk' not in self.kwargs:
                raise Http404('URL is not valid')
            customer = Customer.objects.get_or_none(pk=self.kwargs['pk'])
        # if customer is None:
        #     raise Http404('Page does not exists')
        return customer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['invoices'] = self.object.invoice_set.all().order_by('-id')
            context['payments'] = self.object.payment_set.all().order_by('-id')

        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'invoice/invoice_item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice_seller'] = settings.INVOICE_SELLER

        return context

    def get_object(self):
        user = self.request.user
        if not user.is_staff and not user.is_superuser:
            invoice = Invoice.objects.get_or_none(
                slug=self.kwargs['slug'],
                customer__primary_contact=user
            )
        else:
            invoice = Invoice.objects.get_or_none(slug=self.kwargs['slug'])
        if invoice is None:
            invoice = Invoice()
        return invoice


class CustomerListView(LoginRequiredMixin, PermissionRequiredMixin,
                       ListView):
    model = Customer
    queryset = Customer.objects.all()
    template_name = 'customer/customer_list.html'
    fields = ['name', ]
    extra_context = {
        'breadcrumbs': ['Customer'],
    }
    permission_required = ('customer.view_customer',)

    def get_queryset(self):
        queryset = Customer.objects.all().order_by('-id')

        user = self.request.user
        if not user.is_staff and not user.is_superuser:
            queryset = queryset.filter(
                primary_contact=user
            )

        return queryset


class CustomerCreateView(LoginRequiredMixin, PermissionRequiredMixin,
                         CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customer/customer_form.html'
    permission_required = ('customer.add_customer', )
    extra_context = {
        'form_title': 'New Customer',
        'submit_btn_text': 'Create'
    }

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['form_title'] = 'Create Customer.'
    #     context['submit_btn_text'] = 'Create'
    #     return context

    def get_success_url(self, *args, **kwargs):
        return reverse('customer:customer_home')


class CustomerUpdateView(LoginRequiredMixin, PermissionRequiredMixin,
                         UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customer/customer_form.html'
    permission_required = ('customer.change_customer',)

    def get_success_url(self, *args, **kwargs):
        return reverse("customer:customer_home")


class InvoiceListView(LoginRequiredMixin, PermissionRequiredMixin,
                      ListView):
    model = Invoice
    queryset = Invoice.objects.all()
    template_name = 'invoice/invoice_list.html'
    fields = ['name', ]
    extra_context = {
        'breadcrumbs': ['Invoice'],
    }
    permission_required = ('customer.view_invoice',)

    def get_queryset(self):
        queryset = Invoice.objects.all().order_by('-id')

        user = self.request.user
        if not user.is_staff and not user.is_superuser:
            queryset = queryset.filter(
                customer__primary_contact=user
            )

        return queryset


class InvoiceCreateView(LoginRequiredMixin, PermissionRequiredMixin,
                        CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoice/invoice_form.html'
    permission_required = ('customer.add_invoice',)

    def get_initial(self):
        initial = super().get_initial()
        initial['invoice_number'] = Invoice.generate_slug()
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create Invoice.'
        context['submit_btn_text'] = 'Create'

        if self.request.POST:
            context['items'] = InvoiceProductFormSet(self.request.POST)
        else:
            context['items'] = InvoiceProductFormSet()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()

        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse('customer:invoice_home')


class InvoiceUpdateView(LoginRequiredMixin, PermissionRequiredMixin,
                        UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoice/invoice_form.html'
    permission_required = ('customer.change_invoice',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Update Invoice.'
        context['submit_btn_text'] = 'Update'

        if self.request.POST:
            context['items'] = InvoiceProductFormSet(
                self.request.POST, instance=self.object)
        else:
            context['items'] = InvoiceProductFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()

        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse("customer:invoice_home")


class UserInvoiceListView(LoginRequiredMixin, SEOMixin, ListView):
    canonical_url = '/invoice/list/'
    model = Invoice
    queryset = Invoice.objects.all()
    template_name = 'invoice/invoice_list.html'
    extra_context = {
        'breadcrumbs': ['Invoice'],
    }

    # permission_required = ('customer.view_invoice', )

    def get_queryset(self):
        user = self.request.user
        queryset = Invoice.objects.filter(customer__primary_contact=user).order_by('-id')
        return queryset


class PaymentListView(LoginRequiredMixin, PermissionRequiredMixin,
                      ListView):
    model = Payment
    queryset = Payment.objects.all()
    template_name = 'payment/payment_list.html'
    fields = ['name', ]
    extra_context = {
        'breadcrumbs': ['Payment'],
    }
    permission_required = ('customer.view_payment',)

    def get_queryset(self):
        queryset = Payment.objects.all().order_by('-id')

        user = self.request.user
        if not user.is_staff and not user.is_superuser:
            queryset = queryset.filter(
                customer__primary_contact=user
            )

        return queryset


class PaymentCreateView(LoginRequiredMixin,
                        PermissionRequiredMixin,
                        TemplateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payment/payment_form.html'
    permission_required = ('customer.add_payment',)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        form.fields['cart'].queryset = Cart.objects.filter(is_open=True)

        context_dict = {
            'form_title': 'New Payment',
            'submit_btn_text': 'Create',
            'form': form
        }
        return render(request, self.template_name, context=context_dict)

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data

            cart = data.pop('cart')

            invoice = Invoice.create(cart)
            payment = Payment.create(invoice)

            [setattr(payment, k, v) for k, v in data.items() if k in payment.__dict__]
            payment.save()

            return HttpResponseRedirect(reverse('customer:payment_home'))

        context_dict = {
            'form_title': 'New Payment',
            'submit_btn_text': 'Create',
            'form': form
        }
        return render(request, self.template_name, context=context_dict)


class PaymentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payment/payment_form.html'
    permission_required = ('customer.change_payment', )

    def get(self, request, slug, *args, **kwargs):
        payment = Payment.objects.get_or_none(slug=slug)
        if not payment or not payment.invoice.cart:
            raise Http404('Cart is not exists')

        initial = payment.to_dict()
        initial['cart'] = payment.invoice.cart.id

        form = self.form_class(initial=initial)
        form.fields['cart'].queryset = Cart.objects.filter(id=payment.invoice.cart.id)

        context_dict = {
            'form_title': 'Update Payment',
            'submit_btn_text': 'Update',
            'form': form
        }
        return render(request, self.template_name, context=context_dict)

    def post(self, request, slug, *args, **kwargs):
        payment = Payment.objects.get_or_none(slug=slug)
        if not payment:
            raise Http404('Cart is not exists')

        form = self.form_class(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data

            [setattr(payment, k, v) for k, v in data.items() if k in payment.__dict__]
            payment.save()

            return HttpResponseRedirect(reverse('customer:payment_home'))

        context_dict = {
            'form_title': 'Update Payment',
            'submit_btn_text': 'Update',
            'form': form
        }
        return render(request, self.template_name, context=context_dict)


class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payment/payment_item.html'

    def get_object(self):
        user = self.request.user
        if not user.is_staff and not user.is_superuser:
            payment = Payment.objects.get_or_none(
                slug=self.kwargs['slug'],
                customer__primary_contact=user
            )
        else:
            payment = Payment.objects.get_or_none(slug=self.kwargs['slug'])
        if payment is None:
            payment = Payment()
        return payment


class UserPaymentListView(LoginRequiredMixin, SEOMixin, ListView):
    canonical_url = '/payment/list/'
    model = Payment
    queryset = Payment.objects.all()
    template_name = 'payment/user_payment_list.html'
    extra_context = {
        'breadcrumbs': ['Payment'],
    }

    # permission_required = ('customer.view_invoice', )

    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.filter(customer__primary_contact=user).order_by('-id')
        return queryset


@login_required
def getcustomers(request):
    if not request.user.is_superuser:
        return

    cust_data = []
    search = request.GET.get('q', None)
    if search:
        cust_data = Customer.objects.filter(Q(name__icontains=search) | Q(
            primary_contact__email__icontains=search)).values('id', 'name')
    return JsonResponse(list(cust_data), safe=False)


@login_required
def getinvoice_by_customer(request, customer_id: int):
    if not request.user.is_superuser:
        return

    invoices = Invoice.objects.filter(customer=customer_id).order_by('-id')
    # invoices_data = list(invoices.values('id', 'invoice_number'))
    invoices_data = [{'id': i.id, 'invoice_number': i.__str__()} for i in invoices]

    return JsonResponse({'data': invoices_data})


@login_required
def getopen_cart_by_customer(request, customer_id: int):
    if not request.user.is_superuser:
        return

    carts = Cart.objects.filter(customer=customer_id, is_open=True).order_by('-id')
    carts_data = [{'id': i.id, 'name': '%s %s' % (i.slug, i.total_amount)} for i in carts]

    return JsonResponse({'data': carts_data})


@login_required
def getaddress_by_user(request, user_id: int):
    if not request.user.is_superuser:
        return

    address = Address.objects.filter(user=user_id).order_by('-id')
    address_data = list(address.values('id', 'address', 'city'))

    return JsonResponse({'data': address_data})


@login_required
def getproduct_by_id(request, product_id: int):
    # if not request.user.is_superuser:
    #     return

    prod = Product.objects.get(pk=product_id)
    gst = prod.amount * settings.PRODUCT_GST_PERCENT / 100
    json_data = {
        'amount': round(prod.amount, 2),
        'gst': round(gst, 2),
        'category': prod.category,
        'addon_id': prod.addon.id if prod.addon else None,
        'addon_description': prod.addon.description if prod.addon else None,
    }
    return JsonResponse(json_data)


@login_required
@csrf_exempt
def cart_validation(request, ivrid: int):
    user = request.user
    ivr = IVRConfig.getbyid(user, ivrid)

    check_for = request.POST.get('check_for')
    products = request.POST.getlist('products', [])
    products = list(map(int, products))

    products_qr = Product.objects.filter(
        id__in=products, category="plan"
    )

    json_data = {}
    if check_for == 'has-paid-plan':
        has_active_paid_ivr = ivr.config_type.name != 'free' \
            and (ivr.end_date is None or ivr.end_date >= timezone.now().date())

        paid_item_selected = products_qr.filter(amount__gte=1).exists()

        json_data['paid_plan_found'] = has_active_paid_ivr or paid_item_selected
    elif check_for == 'has-more-plan-item':
        json_data['has_more_plan_item'] = True if products_qr.count() >= 2 else False

    return JsonResponse(json_data)


class KYCView(LoginRequiredMixin, SEOMixin, TemplateView):
    model = Customer
    form_class = KYCForm
    template_name = 'customer/kyc_form.html'

    def get_initial(self, request, user):
        initial = {
            'contact_name': user.first_name + ' ' + user.last_name if user.first_name and
            user.last_name else
            user.first_name,
            'phone': user.profile.phone,
            'email': user.email,
        }

        cust = Customer.objects.get_or_none(primary_contact=user)

        if cust:
            initial.update({
                'slug': cust.slug,
                'name': cust.name,
                'contact_name': cust.contact_name,
                'phone': cust.phone,
                'email': cust.email,
                'gstin': cust.gstin,
                'pan': cust.pan,
            })

            if cust.billing_address:
                initial.update({
                    'billing_address': cust.billing_address.address,
                    'billing_city': cust.billing_address.city,
                    'billing_state': cust.billing_address.state,
                    'billing_pincode': cust.billing_address.pincode,
                    'billing_country': cust.billing_address.country,
                })

            if cust.shipping_address:
                initial.update({
                    'shipping_address': cust.shipping_address.address,
                    'shipping_city': cust.shipping_address.city,
                    'shipping_state': cust.shipping_address.state,
                    'shipping_pincode': cust.shipping_address.pincode,
                    'shipping_country': cust.shipping_address.country,
                })

            if cust.billing_address_id == cust.shipping_address_id:
                initial.update({
                    'same_as_billing_address': True,
                })
            else:
                initial.update({
                    'same_as_billing_address': False,
                })

        return initial

    def get(self, request, userid=None, *args, **kwargs):
        user = request.user
        if userid and (user.is_staff or user.is_superuser):
            user = User.objects.get(pk=userid)
        initial = self.get_initial(request, user)
        context_dict = {
            'form_title': 'KYC.',
            'submit_btn_text': 'Submit',
            'first_name': user.first_name,
            'last_name': user.last_name,
            'slug': initial.get('slug', None),
            'form': self.form_class(user, initial=initial)
        }
        return render(request, self.template_name, context=context_dict)

    def post(self, request, userid=None, *args, **kwargs):
        user = request.user
        if userid and (user.is_staff or user.is_superuser):
            user = User.objects.get(pk=userid)
        form = self.form_class(user, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data

            billing_address, created = Address.objects.get_or_create(
                user=user,
                address=data.get('billing_address', None),
                city=data.get('billing_city', None),
                state=data.get('billing_state', None),
                country=data.get('billing_country', None),
                pincode=data.get('billing_pincode', None),
            )

            same_as_billing_address = data.get('same_as_billing_address', True)
            shipping_address = None
            if same_as_billing_address:
                shipping_address = billing_address
            else:
                shipping_address, created = Address.objects.get_or_create(
                    user=user,
                    address=data.get('shipping_address', None),
                    city=data.get('shipping_city', None),
                    state=data.get('shipping_state', None),
                    country=data.get('shipping_country', None),
                    pincode=data.get('shipping_pincode', None),
                )

            customer_obj = Customer.objects.get_or_none(primary_contact=user)
            if not customer_obj:
                customer_obj, created = Customer.objects.get_or_create(
                    primary_contact=user,
                )
            json_data = dict(
                email=data.get('email', None),
                phone=data.get('phone', None),
                name=data.get('name', None),
                contact_name=data.get('contact_name', None),
                gstin=data.get('gstin', None),
                pan=data.get('pan', None),
                billing_address=billing_address,
                shipping_address=shipping_address,
            )
            for key, value in json_data.items():
                setattr(customer_obj, key, value)
            customer_obj.users.add(user)
            customer_obj.save()

            next = request.GET.get('next', None)
            if next and (
                    customer_obj.gstin not in ['', None] or customer_obj.pan not in ['', None]):
                return HttpResponseRedirect(next)

            # messages.success(request, "KYC saved successfully")
        context_dict = {
            'form_title': 'KYC.',
            'submit_btn_text': 'Submit',
            'first_name': user.first_name,
            'last_name': user.last_name,
            'form': form
        }
        return render(request, self.template_name, context=context_dict)


class CartListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Cart
    queryset = Cart.objects.all()
    template_name = 'cart/cart_list.html'
    fields = ['name', ]
    extra_context = {
        'breadcrumbs': ['Cart'],
    }
    permission_required = ('customer.view_cart',)

    def get_queryset(self):
        queryset = Cart.objects.all().order_by('-dtm_updated')

        user = self.request.user
        if not user.is_staff and not user.is_superuser:
            queryset = queryset.filter(
                customer__primary_contact=user
            )

        return queryset


class CartCreateView(LoginRequiredMixin, PermissionRequiredMixin,
                     CreateView):
    model = Cart
    form_class = CartForm
    template_name = 'cart/cart_form.html'
    permission_required = ('customer.add_cart',)

    def get_initial(self):
        initial = super().get_initial()
        initial['slug'] = Cart.generate_slug()
        initial['invoice_number'] = Invoice.generate_slug()
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create Cart.'
        context['submit_btn_text'] = 'Create'

        if self.request.POST:
            context['items'] = CartProductFormSet(self.request.POST)
        else:
            context['items'] = CartProductFormSet()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()
            else:
                print('----items.errors----', items.errors)

            self.object.reset_items()

        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse('customer:cart_home')


class CartItemPage(LoginRequiredMixin, SEOMixin, TemplateView):
    model = Cart
    template_name = 'cart/cart_item_page.html'
    extra_context = {
        'form_title': None,
        'submit_btn_text': 'Save'
    }

    def get_object(self):
        cart = getcart(self.request, **self.kwargs)
        return cart

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            nextitem = '?next='+reverse('customer:cart_edit')
            return HttpResponseRedirect(reverse('login')+nextitem)

        # if not user.is_staff and not user.is_superuser:
        customer = get_customer(user)
        if not customer or (customer.gstin is None and customer.pan is None):
            nextitem = '?next='+reverse('customer:cart_edit')
            return HttpResponseRedirect(reverse('customer:account_kyc')+nextitem)

        if not self.get_object():
            # ivrid = IVRConfig.getivr_id(user)
            # payload = {'ivrid': ivrid, 'create_with_no_item': True}
            # result = create_subscription_cart(payload)
            customer = get_customer(user)
            cart, created = Cart.objects.get_or_create(
                is_open=True,
                customer=customer,
            )

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = self.request.user

        products = Product.objects.filter(is_active=True)\
            .order_by('-category', 'addon', 'amount', 'id')

        cart = self.get_object()
        print('cart id =', cart.id)

        plan_products = products.filter(category="plan")

        # get last paid plan
        last_plan_prod = InvoiceProduct.objects.filter(
            # ivr=ivr,
            product__category__iexact='plan',
            product__amount__gte=1,
            invoice__payment__is_processed=True
        ).order_by('id').last()

        last_plan_product_id = None
        if last_plan_prod and plan_products.filter(id=last_plan_prod.product.id).exists():
            last_plan_product_id = last_plan_prod.product.id

        disabled_plan_products = []
        if last_plan_product_id:
            for plan_product in plan_products:
                if plan_product.id == last_plan_product_id:
                    break
                else:
                    disabled_plan_products.append(plan_product.id)

        data = {
            "cart": cart,
            # "has_existing_paid_plan": has_existing_paid_plan,
            "last_plan_product_id": last_plan_product_id,
            "disabled_plan_products": disabled_plan_products,
            "products": {
                "plan": plan_products,
                "minutes": products.filter(category="minutes"),
                "agent": products.filter(category="feature", sku__istartswith="AGENT").last(),
                "recording": products.filter(category="feature", sku__istartswith="RECORD").last(),
            }
        }

        checkout_json = {
            "plan": {},
            "minutes": {},
            "agent": {},
            "recording": {}
        }

        for item in cart.items.all():
            key = item.product.id
            category = item.product.category.lower()
            if category in ["plan", "minutes"]:
                checkout_json[category][key] = item.qty
            elif category == "feature":
                if "recording" in item.product.description.lower():
                    checkout_json["recording"][key] = item.qty
                elif "agent" in item.product.description.lower():
                    checkout_json["agent"][key] = item.qty

        # if plan is not added in cart then add default plan product check if no paid plan exists with ivr
        if len(checkout_json["plan"]) == 0:
            plan_product_id = None
            # choose last purchased plan if exists
            if last_plan_product_id:
                plan_product_id = last_plan_product_id

            # choose plan product based on category if exists
            if not plan_product_id:
                ivr_config_product = plan_products.filter(
                    # config_type=ivr.config_type
                ).order_by('id').last()
                if ivr_config_product:
                    plan_product_id = ivr_config_product.id

            # choose last plan product
            if not plan_product_id and plan_products:
                plan_product_id = plan_products.last().id

            if plan_product_id:
                checkout_json["plan"][plan_product_id] = 1

        data["initial"] = checkout_json
        print("checkout_json =", checkout_json)

        # TODO: add current plan and validate frontend

        context = self.get_context_data(**kwargs)
        data.update(context)

        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = json.loads(request.body)
        print(f'post data = {data}')
        submit_btn = data.pop('submit', '')

        cart = self.get_object()
        print('cart id =', cart.id)

        cart.items.all().delete()

        for cat, val in data.items():
            for p_id, qty in val.items():
                product = Product.objects.get(pk=p_id)
                cart.create_item(
                    # ivr,
                    product,
                    qty
                )

        json_data = {'success': True}

        if 'payment' == submit_btn and cart.total_amount >= 1:
            # amount should be mroe than 1
            json_data['next'] = reverse("customer:payment", kwargs={'slug': cart.slug})
        elif not user.is_staff and not user.is_superuser:
            json_data['next'] = reverse("customer:cart_edit")
        else:
            json_data['next'] = reverse("customer:cart_home")

        return JsonResponse(json_data)


def get_customer(user):
    customer = Customer.objects.get_or_none(primary_contact=user)
    return customer


def getcart(request, **kwargs):
    user = request.user

    if (user.is_staff or user.is_superuser) and ('pk' in kwargs):
        cartid = kwargs['pk']
        cart = Cart.objects.get_or_none(pk=cartid)
    else:
        customer = get_customer(user)
        cart = Cart.get_cart_object(customer)

    if cart:
        cart.remove_inactive_product()

    return cart


class UserAutocomplete(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        user_data = []
        search = request.GET.get('q', None)
        if search:
            user_data = User.objects.filter(Q(first_name__icontains=search) | Q(
                email__icontains=search)).values('id', 'email')
        return JsonResponse(list(user_data), safe=False)
