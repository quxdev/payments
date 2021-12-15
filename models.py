import datetime
import importlib
# import uuid
from django.forms.models import model_to_dict
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import RegexValidator
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.template import Context, loader, Template
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage

from qux.utils.phone import phone_number
from qux.utils.date import eomonth
from qux.models import CoreModel, CoreModelPlus, default_null_blank


def get_current_domain():
    current_site = Site.objects.get_current()
    domain = f"https://{current_site.domain}"  # 'https://qux.dev'
    if '127.0.0.1:8000' in domain:
        domain = f"http://{current_site.domain}"
    return domain


class OnPaymentSuccess:
    def __init__(self, payment_obj):
        self.payment_obj = payment_obj

    def process(self):
        print("OnPaymentSuccess process(), payment_obj: ", self.payment_obj)
        # ModelNameToCreate.create(self.payment_obj)

        return True


class Address(CoreModelPlus):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address = models.TextField(**default_null_blank)
    city = models.CharField(max_length=128, **default_null_blank)
    state = models.CharField(max_length=128, **default_null_blank)
    pincode = models.CharField(max_length=8, **default_null_blank)
    country = models.CharField(max_length=128, **default_null_blank)

    def __str__(self):
        return '%s : %s : %s' % (self.id, self.city, self.address)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def get_full_address(self):
        arr = [self.address, self.city, self.state, self.pincode, self.country]
        arr = [i for i in arr if i]

        if len(arr) == 0:
            return None
        return ', '.join(arr)


class Customer(CoreModel):
    regexp = RegexValidator(
        regex=r'^\+?[1-9]\d{4,14}$',
        message="Phone number must be entered in the format: '+999999999'. "
                "Up to 15 digits allowed."
    )
    gstin_regexp = RegexValidator(
        regex=r'^[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9a-zA-Z]{1}Z|z[0-9a-zA-Z]{1}$',
        message="Enter valid GSTIN number. Up to 15 digits allowed."
    )
    pan_regexp = RegexValidator(
        regex=r'^[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}$',
        message="Enter valid PAN number. Up to 10 digits allowed."
    )

    slug = models.SlugField(max_length=32, unique=True, null=True, default=None)
    name = models.CharField(max_length=128, **default_null_blank, verbose_name='Company Name')
    contact_name = models.CharField(max_length=128, **default_null_blank)
    billing_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, related_name='billing_customers',
        **default_null_blank)
    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, related_name='shipping_customers',
        **default_null_blank)
    # Comma separated list of phone numbers
    phone = models.CharField(max_length=255)
    # Comma separated list of email addresses
    email = models.CharField(max_length=255)
    gstin = models.CharField(
        max_length=15, validators=[gstin_regexp], **default_null_blank,
        verbose_name='GSTIN',
    )
    pan = models.CharField(
        max_length=10, validators=[pan_regexp], **default_null_blank,
        verbose_name='PAN',
    )
    gstin_verified = models.BooleanField(default=False, verbose_name='GSTIN Verified')
    pan_verified = models.BooleanField(default=False, verbose_name='PAN Verified')
    primary_contact = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='primay_customer', verbose_name='Primary Contact')
    users = models.ManyToManyField(User, blank=True, related_name='users_customers')
    website = models.URLField(default=None, blank=True, null=True)
    whatsapp = models.CharField(
        max_length=16, validators=[regexp],
        default=None, blank=True, null=True, verbose_name='WhatsApp'
    )

    def __init__(self, *args, **kwargs):
        super(Customer, self).__init__(*args, **kwargs)
        self.old_pan = self.pan

    def clean(self):
        if self.pan:
            qs = self.__class__.objects.filter(
                pan=self.pan
            ).exclude(id=self.pk)
            if qs.exists():
                raise ValidationError({
                    "pan": "Pan number is already in use. Please enter another Pan number."
                })

    def __str__(self):
        return '%s' % (self.name)

    def save(self, *args, **kwargs):
        if self.phone:
            phones = self.phone.split(',')
            valid_phones = []
            for phone in phones:
                valid_phone = phone_number(phone)
                if valid_phone:
                    valid_phones.append(valid_phone)
            self.phone = ','.join(valid_phones)
        if self.email:
            emails = self.email.split(',')
            self.email = ','.join(emails)
        if self.gstin:
            self.gstin = self.gstin.upper()
        if self.pan:
            self.pan = self.pan.upper()

        if not self.slug:
            # Generate ID once, then check the db. If exists, keep trying.
            self.slug = 'cus_'+get_random_string(16)
            while self.__class__.objects.filter(slug=self.slug).exists():
                self.slug = 'cus_'+get_random_string(16)

        super().save(*args, **kwargs)

    def to_data(self):
        exclude = ['dtm_created', 'dtm_updated', 'website', 'whatsapp', 'users', 'billing_address',
                   'shipping_address', 'gstin', 'gstin_verified', 'pan', 'pan_verified']

        all_values = super().to_dict(verbose_name=True, exclude=exclude)

        slug_url = f'{get_current_domain()}{reverse("customer:customer_edit", args=(self.slug,))}'
        all_values['url'] = slug_url
        all_values['primary_contact'] = self.primary_contact.email

        if self.gstin:
            all_values['gstin'] = self.gstin + ' ' + \
                ('Verified' if self.gstin_verified else 'Not Verified')
        elif self.pan:
            all_values['pan'] = self.pan + ' ' + \
                ('Verified' if self.pan_verified else 'Not Verified')

        return all_values

    def to_text(self):
        email_data = {
            'data': [
                {
                    'title': 'Customer',
                    'all_values': self.to_data()
                },
            ]
        }

        message = loader.render_to_string(
            'email/billing_action.html', email_data)

        return message


@receiver(post_save, sender=Customer)
def customer_postsave(sender, instance, created, **kwargs):
    if not settings.KYC_GST_PAN_REQUIRED and created:
        send_email_on_new_customer(instance)

    elif instance.pan and instance.old_pan != instance.pan and instance.old_pan in ['', None]:
        send_email_on_new_customer(instance)


def send_email_on_new_customer(customer_obj):
    subject = f"New Customer: {str(customer_obj.primary_contact.email)}"

    message = customer_obj.to_text()

    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL,
                         settings.TEAM_SALES)
    email.content_subtype = 'html'
    res = email.send()
    print('send_email_on_new_customer res =', res)

    return True


class CartInvoice(CoreModel):
    slug = models.SlugField(max_length=32, unique=True, null=True, default=None)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    invoice_number = models.CharField(max_length=20, unique=True)
    invoice_date = models.DateField(**default_null_blank)
    due_date = models.DateField(**default_null_blank)  # invoice expire.
    amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    gst = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    billing_address = models.TextField(**default_null_blank)
    shipping_address = models.TextField(**default_null_blank)

    class Meta:
        abstract = True


class Cart(CartInvoice):
    is_open = models.BooleanField(default=True)

    class Meta:
        # not works on MySWL for Django 3.1
        constraints = [
            models.UniqueConstraint(fields=['customer'], condition=Q(
                is_open=True), name='unique_customer_is_open')
        ]

    def __str__(self):
        return '%s : %s : %s' % (self.is_open, self.total_amount, self.customer_id)

    def save(self, *args, **kwargs):
        self.total_amount = self.amount + self.gst
        if not self.billing_address and self.customer.billing_address:
            self.billing_address = self.customer.billing_address.get_full_address()
        if not self.shipping_address and self.customer.shipping_address:
            self.shipping_address = self.customer.shipping_address.get_full_address()
        if not self.slug:
            self.slug = self.__class__.generate_slug()
        if not self.invoice_number:
            self.invoice_number = Invoice.generate_slug()

        super().save(*args, **kwargs)

    @staticmethod
    def generate_slug():
        slug = 'crt_'+get_random_string(16)
        while Cart.objects.filter(slug=slug).exists():
            slug = 'crt_'+get_random_string(16)

        return slug

    def create_item(self, product, qty=1):
        item, created = CartProduct.objects.update_or_create(
            cart=self,
            product=product,
            qty=qty,
            # unit_price=product.amount,
        )

        return item

    @classmethod
    def create(cls, customer, product):
        cart_obj = cls.objects.filter(customer=customer, is_open=True).last()

        print('last cart =', cart_obj)

        if cart_obj:
            # cart_obj.items.all().delete()
            cart_obj.items.filter(
                product__category__iexact='plan'
            ).delete()
        else:
            invoice_number = Invoice.generate_slug()

            cart_obj = cls.objects.create(
                customer=customer,
                invoice_number=invoice_number
            )

        cart_obj.create_item(product)

        return cart_obj

    def update_amount(self):
        self.amount = 0
        self.gst = 0
        for item_obj in self.items.all():
            self.amount += item_obj.amount
            self.gst += item_obj.gst

        self.save()

    def reset_addon(self):
        # remove those addon whose parent not added
        for item_obj in self.items.all():
            if item_obj.product.addon:
                if not self.items.filter(product=item_obj.product.addon).exists():
                    item_obj.delete()

    def reset_minute_feature_plan(self):
        # remove minutes if paid plan is not exists
        for item_obj in self.items.all():
            if item_obj.product.category in ['minutes', 'feature']:
                has_plan_item = self.items.filter(
                    product__category='plan', amount__gte=1
                ).exists()
                if not has_plan_item:
                    item_obj.delete()

    def reset_to_one_plan(self):
        plan_items = self.items.filter(product__category='plan').order_by('dtm_updated')
        total_plan_items = plan_items.count()
        if total_plan_items >= 2:
            # latest_id = plan_items.last().id
            # for item in plan_items.exclude(pk=latest_id):
            for item in plan_items[:total_plan_items-1]:
                item.delete()

    def remove_inactive_product(self):
        inactive_products = self.items.filter(product__is_active=False)
        if inactive_products.count() > 0:
            inactive_products.delete()

    def reset_items(self):
        self.reset_addon()
        self.reset_minute_feature_plan()
        self.reset_to_one_plan()
        self.remove_inactive_product()

    def swipez_payload(self):
        user = self.customer.primary_contact

        addressObj = None
        if self.customer.billing_address:
            addressObj = self.customer.billing_address

        webhook = reverse('customer:webhook', kwargs={'reference': self.slug})
        result = {
            'account_id': 'M000000041',
            'return_url': webhook,
            'reference_no': self.slug,
            'description': '',
            'amount': '{:.2f}'.format(self.total_amount),
            'name': f'{user.first_name} {user.last_name}',
            'address': addressObj.address if addressObj else None,
            'city': addressObj.city if addressObj else None,
            'state': addressObj.state if addressObj else None,
            'postal_code': addressObj.pincode if addressObj else None,
            'phone': self.customer.phone[-10:],
            'email': user.email,
        }

        return result

    def razorpay_payload(self):
        jsondata = {
            'amount': int(self.total_amount * 100),
            'currency': settings.PAYMENT_CURRENCY,
            'receipt': self.slug,
        }
        return jsondata

    def stripe_payload(self):
        jsondata = {
            'amount': int(self.total_amount * 100),
            'currency': settings.PAYMENT_CURRENCY,
            'receipt': self.slug,
        }
        return jsondata

    def to_data(self):
        exclude = ['id', 'dtm_created', 'dtm_updated', 'billing_address', 'shipping_address',
                   'customer']

        all_values = super().to_dict(verbose_name=True, exclude=exclude)
        all_values['user_email'] = self.customer.primary_contact.email
        all_values['user_phone'] = self.customer.phone

        if not self.invoice_date and 'invoice_date' in all_values:
            del all_values['invoice_date']
        if not self.due_date and 'due_date' in all_values:
            del all_values['due_date']

        return all_values

    def to_text(self):
        email_data = {
            'data': [
                {
                    'title': 'Cart',
                    'all_values': self.to_data()
                },
                {
                    'title': 'Customer',
                    'all_values': self.customer.to_data()
                },
            ]
        }

        for item in self.items.all():
            item_data = item.to_data()
            email_data['data'].append({
                'title': f'Cart Item - {item_data["product"]}',
                'all_values': item_data
            })

        message = loader.render_to_string(
            'email/billing_action.html', email_data)

        return message

    @classmethod
    def get_cart_object(cls, customer):
        cart = None

        no_of_carts = Cart.objects.filter(
            customer=customer,
            is_open=True
        )

        if no_of_carts.count() == 1:
            cart = no_of_carts.first()
        else:
            for non_sub in no_of_carts:
                if non_sub.items.count() > 0:
                    cart = non_sub
                    break

            if cart is None:
                cart = no_of_carts.first()

        print('cart =', cart)
        return cart


class Invoice(CartInvoice):
    cart = models.ForeignKey(Cart, on_delete=models.DO_NOTHING, **default_null_blank)

    def __str__(self):
        return '%s : %s : %s' % (self.invoice_number, self.total_amount, self.customer_id)

    def save(self, *args, **kwargs):
        self.total_amount = self.amount + self.gst
        if not self.billing_address and self.customer.billing_address:
            self.billing_address = self.customer.billing_address.get_full_address()
        if not self.shipping_address and self.customer.shipping_address:
            self.shipping_address = self.customer.shipping_address.get_full_address()
        if not self.slug:
            self.slug = self.__class__.generate_slug()

        super().save(*args, **kwargs)

    @staticmethod
    def generate_slug():
        slug = 'inv_'+get_random_string(16)
        while Invoice.objects.filter(slug=slug).exists() \
                or Cart.objects.filter(invoice_number=slug).exists():
            slug = 'inv_'+get_random_string(16)

        return slug

    def dict(self):
        items = []

        for item in self.items.all():
            items.append({
                'product_name': item.product.sku if item.product else None,
                'amount': item.amount,
                'gst': item.gst,
            })

        jsondata = {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'invoice_date': self.invoice_date,
            'due_date': self.due_date,
            'amount': self.amount,
            'gst': self.gst,
            'total_amount': self.total_amount,
            'items': items,
        }
        return jsondata

    def paid_amount(self):
        result = sum([x.paid_amount for x in self.payment_set.filter(is_processed=True)])
        return result

    def unpaid(self):
        return self.total_amount - Decimal(self.paid_amount())

    def update_amount(self):
        self.amount = 0
        self.gst = 0
        for item_obj in self.items.all():
            self.amount += item_obj.amount
            self.gst += item_obj.gst

        self.save()

    @classmethod
    def create(cls, cart):
        slug = Invoice.generate_slug()
        json_data = dict(
            customer=cart.customer,
            invoice_number=cart.invoice_number if cart.invoice_number else slug,
            slug=cart.invoice_number if 'inv_' in cart.invoice_number else slug,
            cart=cart,
        )

        invoice_obj, created = Invoice.objects.get_or_create(
            **json_data
        )

        # for key, value in json_data.items():
        #     setattr(invoice_obj, key, value)
        # invoice_obj.save()

        invoice_obj.invoice_date = cart.invoice_date
        invoice_obj.due_date = cart.due_date
        if not invoice_obj.invoice_date:
            invoice_obj.invoice_date = timezone.now().today().date()
        if not invoice_obj.due_date:
            invoice_obj.due_date = timezone.now().today().date()
        invoice_obj.save()

        for item in cart.items.all():
            InvoiceProduct.objects.get_or_create(
                invoice=invoice_obj,
                product=item.product,
                unit_price=item.unit_price,
                unit_gst=item.unit_gst,
                amount=item.amount,
                gst=item.gst,
                total_amount=item.total_amount,
                qty=item.qty,
                sac_code=item.sac_code,
            )

        return invoice_obj

    def to_data(self):
        exclude = ['id', 'dtm_created', 'dtm_updated', 'billing_address', 'shipping_address',
                   'customer', 'cart']

        all_values = super().to_dict(verbose_name=True, exclude=exclude)
        slug_url = f'{get_current_domain()}{reverse("customer:invoice_detail", args=(self.slug,))}'
        all_values['url'] = slug_url

        if not self.invoice_date and 'invoice_date' in all_values:
            del all_values['invoice_date']
        if not self.due_date and 'due_date' in all_values:
            del all_values['due_date']

        return all_values

    def to_text(self):
        email_data = {
            'data': [
                {
                    'title': 'Invoice',
                    'all_values': self.to_data()
                },
                {
                    'title': 'Cart',
                    'all_values': self.cart.to_data()
                },
                {
                    'title': 'Customer',
                    'all_values': self.customer.to_data()
                },
            ]
        }

        message = loader.render_to_string(
            'email/billing_action.html', email_data)

        return message


class Payment(CoreModel):
    PAYMENT_MODE = (
        ('Cash', 'Cash'),
        ('Bank Remittance', 'Bank Remittance'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Wallet', 'Wallet'),
        ('Online', 'Online'),
    )
    PAYMENT_SOURCE = (
        ('GooglePay', 'GooglePay'),
        ('Swipez', 'Swipez'),
        ('Stripe', 'Stripe'),
        ('RazorPay', 'RazorPay'),
        ('Paytm', 'Paytm'),
    )
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # two blank value can not allow in unique field
    slug = models.SlugField(max_length=32, unique=True, null=True, default=None)
    invoice = models.ForeignKey(Invoice, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    payment_date = models.DateField(**default_null_blank)
    payment_mode = models.CharField(max_length=16, choices=PAYMENT_MODE)
    payment_source = models.CharField(max_length=16, choices=PAYMENT_SOURCE, **default_null_blank)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    source_reference = models.CharField(max_length=32, **default_null_blank)

    is_processed = models.BooleanField(default=False)  # is paid
    new_object_id = models.CharField(max_length=64, **default_null_blank)
    post_dict = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return '%s : %s' % (self.invoice.invoice_number, self.payment_date)

    def __init__(self, *args, **kwargs):
        super(Payment, self).__init__(*args, **kwargs)
        self.old_is_processed = self.is_processed
        self.old_payment_date = self.payment_date

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate ID once, then check the db. If exists, keep trying.
            self.slug = 'pmt_'+get_random_string(16)
            while self.__class__.objects.filter(slug=self.slug).exists():
                self.slug = 'pmt_'+get_random_string(16)
        self.customer = self.invoice.customer

        super(Payment, self).save(*args, **kwargs)

    @classmethod
    def create(cls, invoice):
        if invoice.unpaid() == 0:
            return None

        obj = cls()
        obj.invoice = invoice
        obj.payment_mode = 'Online'
        obj.payment_source = settings.PAYMENT_PROVIDER
        obj.paid_amount = invoice.unpaid()
        # reference = invoice.reference[:12] + '{:06x}'.format(invoice.id)
        # obj.reference = reference.upper()
        # obj.webhook = f"/customer/payment/webhook/{obj.reference}/"
        obj.save()

        return obj

    def to_data(self):
        exclude = ['id', 'dtm_created', 'dtm_updated', 'invoice', 'customer', 'new_object_id',
                   'post_dict']

        all_values = super().to_dict(verbose_name=True, exclude=exclude)
        slug_url = f'{get_current_domain()}{reverse("customer:payment_detail", args=(self.slug,))}'
        all_values['url'] = slug_url

        return all_values

    def to_text(self):
        email_data = {
            'data': [
                {
                    'title': 'Payment',
                    'all_values': self.to_data()
                },
                {
                    'title': 'Cart',
                    'all_values': self.invoice.cart.to_data()
                },
                {
                    'title': 'Customer',
                    'all_values': self.invoice.customer.to_data()
                },
            ]
        }

        for item in self.invoice.cart.items.all():
            item_data = item.to_data()
            email_data['data'].append({
                'title': f'Cart Item - {item_data["product"]}',
                'all_values': item_data
            })

        message = loader.render_to_string(
            'email/billing_action.html', email_data)

        return message


def get_expiry_date(expiry_date, n: int):
    """
    n: number of months to bill for
    """
    todayDate = timezone.now().today().date()
    # if none then today date
    if not expiry_date:
        expiry_date = todayDate
    # if end_date is old and we have to set expiry_date as futer date so
    if expiry_date < todayDate:
        expiry_date = todayDate

    # 1. if expiry_date is the first of the month
    if expiry_date.day == 1:
        expiry_date = eomonth(expiry_date, n-1)
    # 2. if expiry_date is the end of the month
    elif expiry_date == eomonth(expiry_date, 0):
        expiry_date = eomonth(expiry_date, n)
    # 3. All other dates
    else:
        next_month = eomonth(expiry_date, n)
        expiry_date = datetime.date(next_month.year, next_month.month, expiry_date.day - 1)
    return expiry_date


@receiver(post_save, sender=Payment)
def payment_postsave(sender, instance, created, **kwargs):
    invoice = instance.invoice
    if instance.is_processed and invoice.cart and invoice.cart.is_open:
        invoice.cart.is_open = False
        invoice.cart.save()

    if instance.payment_date and instance.old_payment_date != instance.payment_date:
        if not invoice.invoice_date and not invoice.due_date:
            invoice.invoice_date = invoice.due_date = instance.payment_date
            invoice.save()

    if instance.is_processed and not instance.new_object_id and instance.source_reference != 'csv':
        user = invoice.customer.primary_contact

        # this will call class and pass user value on class initialization
        mod_name, func_name = settings.ON_PAYMENT_SUCCESS.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        clss = getattr(mod, func_name)
        clss(instance).process()


def send_email_for_payment(payment):
    subject = "Payment created: " + str(payment.slug)

    cart = payment.invoice.cart

    message = payment.to_text()

    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL,
                         settings.TEAM_SALES)
    email.content_subtype = 'html'
    res = email.send()
    print('send_email_for_payment res =', res)

    return False


class Product(CoreModel):
    PRODUCT_CATEGORY = (
        ('plan', 'Plan'),
        ('feature', 'Feature'),
        ('minutes', 'Minutes'),
        ('messages', 'Messages'),
        ('custom', 'Custom')
    )
    sku = models.CharField(max_length=8, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    description = models.CharField(max_length=128, default=None, null=True, blank=True)
    category = models.CharField(max_length=16, choices=PRODUCT_CATEGORY)
    monthly_validity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False, verbose_name='Active')
    expiry_date = models.DateField(**default_null_blank, verbose_name='Expiry Date')
    sac_code = models.CharField(max_length=6, **default_null_blank)
    addon = models.ForeignKey("self", on_delete=models.CASCADE,
                              related_name="addons", **default_null_blank)

    class Meta:
        unique_together = [
            ('amount', 'category',
             'monthly_validity', 'is_active')
        ]

    def __str__(self):
        return '%s : %s : %s : %s' % (self.description, self.category, self.id, self.amount)

    @classmethod
    def default_queryset(cls):
        return Product.objects.filter(is_active=True).order_by('-category', 'addon', 'amount', 'id')

    @classmethod
    def plan_queryset(cls):
        products = cls.default_queryset()

        return products.filter(category="plan")

    def total_amount(self):
        gst = self.amount * settings.PRODUCT_GST_PERCENT / 100
        total_amount = self.amount + gst
        return total_amount


class CartInvoiceProduct(CoreModel):
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, **default_null_blank)
    qty = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    unit_gst = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    gst = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    sac_code = models.CharField(max_length=6, **default_null_blank)
    description = models.CharField(max_length=250, **default_null_blank)
    start_date = models.DateField(**default_null_blank, verbose_name='Start Date')
    end_date = models.DateField(**default_null_blank, verbose_name='End Date')

    class Meta:
        abstract = True


class CartProduct(CartInvoiceProduct):
    cart = models.ForeignKey(Cart, on_delete=models.DO_NOTHING, related_name='items')

    def save(self, *args, **kwargs):
        if not self.product:
            return

        if settings.CART_INVOICE_ITEM_CUSTOM_FIELD == False:
            self.unit_price = self.product.amount
            self.unit_gst = self.unit_price * settings.PRODUCT_GST_PERCENT / 100
            self.amount = self.qty * self.unit_price
            self.gst = self.qty * self.unit_gst
            self.total_amount = self.amount + self.gst

        if not self.sac_code:
            self.sac_code = self.product.sac_code

        super().save(*args, **kwargs)

    def __str__(self):
        return '%s : %s : %s' % (self.id, self.cart.invoice_number, self.amount)

    def to_data(self):
        exclude = ['id', 'dtm_created', 'dtm_updated', 'unit_price',
                   'unit_gst', 'description', 'cart', 'product']

        all_values = super().to_dict(verbose_name=True, exclude=exclude, exclude_none=True)
        all_values['product'] = self.product.sku
        all_values['product description'] = self.product.description
        all_values['product category'] = self.product.category

        return all_values


@receiver(post_save, sender=CartProduct)
def cart_items_postsave(sender, instance, **kwargs):
    instance.cart.update_amount()


@receiver(post_delete, sender=CartProduct)
def cart_items_postdelete(sender, instance, **kwargs):
    instance.cart.update_amount()


class InvoiceProduct(CartInvoiceProduct):
    invoice = models.ForeignKey(Invoice, on_delete=models.DO_NOTHING, related_name='items')

    class Meta:
        verbose_name = 'Invoice Detail'

    def __str__(self):
        return '%s : %s : %s' % (self.id, self.invoice.invoice_number, self.amount)


@receiver(post_save, sender=InvoiceProduct)
def inv_items_postsave(sender, instance, **kwargs):
    instance.invoice.update_amount()


@receiver(post_delete, sender=InvoiceProduct)
def inv_items_postdelete(sender, instance, **kwargs):
    instance.invoice.update_amount()
