from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
# from django.utils.safestring import mark_safe

from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['user', 'address', 'city', 'state', 'pincode', 'country']

    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control foo-border'
        })
    )

    address = forms.CharField(
        max_length=10000,
        label='Address',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control foo-border',
                'rows': 6,
                'placeholder': 'Enter Address'
            }
        ),
    )

    city = forms.CharField(
        label='City',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter City'
        })
    )

    state = forms.CharField(
        label='State',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter State'
        })
    )

    pincode = forms.CharField(
        label='Pincode',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Pincode'
        })
    )

    country = forms.CharField(
        label='Country',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Country'
        })
    )


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'name', 'contact_name', 'primary_contact', 'billing_address', 'shipping_address',
            'phone', 'email', 'gstin', 'pan'
        ]
        # widgets = {
        #     'users': forms.SelectMultiple(attrs={
        #         'class': 'form-control foo-border'
        #     })
        # }

    name = forms.CharField(
        label='Company Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Company Name'
        })
    )

    contact_name = forms.CharField(
        label='Contact Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Contact Name'
        })
    )

    primary_contact = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control foo-border custom-select'
        })
    )

    billing_address = forms.ModelChoiceField(
        required=False,
        queryset=Address.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control foo-border custom-select'
        })
    )

    shipping_address = forms.ModelChoiceField(
        required=False,
        queryset=Address.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control foo-border custom-select'
        })
    )

    phone = forms.CharField(
        label='Phone',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Phone'
        })
    )

    email = forms.CharField(
        label='Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Email'
        })
    )

    gstin = forms.CharField(
        required=False,
        label='GSTIN',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter GSTIN'
        })
    )

    pan = forms.CharField(
        required=False,
        label='PAN',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter PAN'
        })
    )

    # users = forms.MultipleChoiceField(
    #     # queryset=User.objects.all(),
    #     widget=forms.SelectMultiple(attrs={
    #         'class': 'form-control foo-border'
    #     })
    # )


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'invoice_number', 'invoice_date', 'due_date']  # , 'amount', 'gst'

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control foo-border custom-select'
        })
    )

    invoice_number = forms.CharField(
        label='Invoice Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Invoice Number'
        })
    )

    invoice_date = forms.DateField(
        label='Invoice Date',
        widget=DateInput(attrs={
            'class': 'form-control foo-border',
            'value': datetime.date.today()
        })
    )

    due_date = forms.DateField(
        label='Due Date',
        widget=DateInput(attrs={
            'class': 'form-control foo-border',
            'value': datetime.date.today()
        })
    )

    # amount = forms.DecimalField(
    #     widget=forms.NumberInput(attrs={
    #         'class': 'form-control foo-border',
    #         'placeholder': 'Enter Amount',
    #         'min': '0',
    #     })
    # )
    #
    # gst = forms.DecimalField(
    #     widget=forms.NumberInput(attrs={
    #         'class': 'form-control foo-border',
    #         'placeholder': 'Enter GST',
    #         'min': '0',
    #     })
    # )


class InvoiceProductForm(forms.ModelForm):
    class Meta:
        model = InvoiceProduct
        exclude = ()

    product = forms.ModelChoiceField(
        required=False,
        queryset=Product.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control foo-border custom-select'
        })
    )

    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Amount',
            'min': '0',
        })
    )

    gst = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter GST',
            'min': '0',
        })
    )


InvoiceProductFormSet = inlineformset_factory(
    Invoice, InvoiceProduct, form=InvoiceProductForm,
    fields=['product', 'amount', 'gst'], extra=1, can_delete=True
)


# class PaymentForm(forms.ModelForm):
class PaymentForm(forms.Form):
    class Meta:
        model = Payment
        fields = [
            'customer', 'cart', 'payment_date', 'payment_mode', 'payment_source',
            'paid_amount', 'source_reference', 'is_processed'
        ]

    customer = forms.ModelChoiceField(
        required=False,
        queryset=Customer.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control foo-border custom-select'
        })
    )

    cart = forms.ModelChoiceField(
        queryset=Cart.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control foo-border custom-select'
        })
    )

    payment_date = forms.DateField(
        label='Payment Date',
        widget=DateInput(attrs={
            'class': 'form-control foo-border',
            'value': datetime.date.today()
        })
    )

    payment_mode = forms.ChoiceField(
        required=False,
        choices=Payment.PAYMENT_MODE,
        widget=forms.Select(attrs={
            'class': 'form-control foo-border custom-select',
            'placeholder': 'Enter Payment Mode'
        })
    )

    payment_source = forms.ChoiceField(
        required=False,
        choices=Payment.PAYMENT_SOURCE + ((None, None),),
        widget=forms.Select(attrs={
            'class': 'form-control foo-border custom-select',
            'placeholder': 'Enter Payment Source'
        })
    )

    paid_amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Paid Amount',
            'min': '0',
        })
    )

    source_reference = forms.CharField(
        required=False,
        label='Source Reference',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Source Reference'
        })
    )

    is_processed = forms.BooleanField(
        required=False,
        label='Is Processed/Paid',
        widget=forms.CheckboxInput()
    )


class KYCForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        gstin = self.cleaned_data.get('gstin')
        pan = self.cleaned_data.get('pan')
        if not gstin and not pan:
            raise forms.ValidationError('Please enter GSTIN or PAN.')

        qs = Customer.objects.filter(
            pan=pan
        ).exclude(primary_contact=self.user)
        if qs.exists():
            raise ValidationError({
                "pan": "Pan number is already in use. Please enter another Pan number."
            })

        return self.cleaned_data

    name = forms.CharField(
        label='Company Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Company Name'
        }),
        max_length=128
    )

    contact_name = forms.CharField(
        label='Contact Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Contact Name'
        }),
        max_length=128
    )

    phone = forms.CharField(
        label='Phone',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Phone'
        }),
        max_length=255
    )

    email = forms.CharField(
        label='Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Email'
        }),
        max_length=255
    )

    gstin = forms.CharField(
        required=False,
        label='GSTIN',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter GSTIN',
            'style': 'text-transform:uppercase'
        }),
        max_length=15, validators=[Customer.gstin_regexp]
    )

    pan = forms.CharField(
        required=False,
        label='PAN',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter PAN',
            'style': 'text-transform:uppercase'
        }),
        max_length=10, validators=[Customer.pan_regexp]
    )

    billing_address = forms.CharField(
        max_length=10000,
        # label=mark_safe('Billing Address:-<br /><br />Address'),
        label='Address',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control foo-border',
                'rows': 4,
                'placeholder': 'Enter Address',
                'group_label': 'Billing Address'
            }
        ),
    )

    billing_city = forms.CharField(
        label='City',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter City'
        }),
        max_length=128
    )

    billing_state = forms.CharField(
        label='State',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter State'
        }),
        max_length=128
    )

    billing_pincode = forms.CharField(
        label='Pincode',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Pincode'
        }),
        max_length=8
    )

    billing_country = forms.CharField(
        label='Country',
        initial='IN',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Country'
        }),
        max_length=128
    )

    same_as_billing_address = forms.BooleanField(
        required=False,
        initial=True,
        # label=mark_safe('Shipping Address:-<br /><br />Same as billing address'),
        label='Same as billing address',
        widget=forms.CheckboxInput(attrs={'group_label': 'Shipping Address'})
    )

    shipping_address = forms.CharField(
        required=False,
        max_length=10000,
        label='Address',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control foo-border',
                'rows': 4,
                'placeholder': 'Enter Address'
            }
        ),
    )

    shipping_city = forms.CharField(
        required=False,
        label='City',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter City'
        }),
        max_length=128
    )

    shipping_state = forms.CharField(
        required=False,
        label='State',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter State'
        }),
        max_length=128
    )

    shipping_pincode = forms.CharField(
        required=False,
        label='Pincode',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Pincode'
        }),
        max_length=8
    )

    shipping_country = forms.CharField(
        required=False,
        label='Country',
        initial='IN',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Country'
        }),
        max_length=128
    )


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['customer', 'slug', 'invoice_number', 'invoice_date',
                  'due_date', 'cart_type']  # , 'amount', 'gst'

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control foo-border custom-select'
        })
    )

    slug = forms.CharField(
        required=False,
        label='Slug',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Slug'
        })
    )

    invoice_number = forms.CharField(
        required=False,
        label='Invoice Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter Invoice Number'
        })
    )

    invoice_date = forms.DateField(
        label='Invoice Date',
        widget=DateInput(attrs={
            'class': 'form-control foo-border',
            'value': datetime.date.today()
        })
    )

    due_date = forms.DateField(
        label='Due Date',
        widget=DateInput(attrs={
            'class': 'form-control foo-border',
            'value': datetime.date.today()
        })
    )

    cart_type = forms.CharField(
        required=False,
        initial='system',
        widget=forms.HiddenInput()
    )


class CartCustomerForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = []
        # fields = ['slug']


class ProductModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        label = '%s (%s) at %s' % (obj.description, obj.category, round(obj.amount, 2))
        if obj.addon:
            label += ' (Add-On of '+obj.addon.description+')'
        return label


class CartProductForm(forms.ModelForm):
    class Meta:
        model = CartProduct
        # exclude = ()
        fields = ['product', 'unit_price', 'unit_gst', 'qty']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_price'].disabled = True
        self.fields['unit_gst'].disabled = True

        if 'unit_price' in self.initial:
            self.initial['unit_price'] = round(self.initial['unit_price'], 2)
        if 'unit_gst' in self.initial:
            self.initial['unit_gst'] = round(self.initial['unit_gst'], 2)

    product = ProductModelChoiceField(
        required=False,
        queryset=Product.objects.filter(is_active=True).order_by(
            '-category', 'addon', 'amount', 'id'),
        widget=forms.Select(attrs={
            'class': 'form-control foo-border custom-select'
        })
    )

    unit_price = forms.DecimalField(
        required=False,
        label='Unit Price',
        widget=forms.NumberInput(attrs={
            'class': 'form-control foo-border',
            'readonly': True,
        })
    )

    unit_gst = forms.DecimalField(
        required=False,
        label='Unit GST',
        widget=forms.NumberInput(attrs={
            'class': 'form-control foo-border',
            'readonly': True,
        })
    )

    qty = forms.IntegerField(
        initial=1,
        label='Quantity',
        widget=forms.NumberInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Quantity',
            'min': '1',
        })
    )


CartProductFormSet = inlineformset_factory(
    Cart, CartProduct, form=CartProductForm,
    fields=['product', 'unit_price', 'unit_gst', 'qty'], extra=1, can_delete=True
)
