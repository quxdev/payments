from django.contrib import admin

from qux.models import CoreModelAdmin
from .models import *


class ProductAdmin(CoreModelAdmin):
    list_display = ('id', 'sku', 'amount', 'monthly_validity', 'description',
                    'category', 'is_active', 'expiry_date', 'sac_code') + CoreModelAdmin.list_display
    search_fields = ('id', 'sku', 'amount', 'monthly_validity', 'description',
                     'category', 'is_active', 'expiry_date', 'sac_code')
    raw_id_fields = ('addon', )


admin.site.register(Product, ProductAdmin)


class CustomerAdmin(CoreModelAdmin):
    list_display = ('id', 'name', 'contact_name', 'primary_contact', 'gstin', 'pan',
                    'gstin_verified', 'pan_verified',) + CoreModelAdmin.list_display
    search_fields = ('id', 'name', 'contact_name', 'primary_contact__username', 'gstin', 'pan', )
    raw_id_fields = ('primary_contact', 'users', 'billing_address', 'shipping_address')


admin.site.register(Customer, CustomerAdmin)


class InvoiceProductInline(admin.TabularInline):
    model = InvoiceProduct
    show_change_link = True
    extra = 0
    raw_id_fields = ('product', )


class InvoiceAdmin(CoreModelAdmin):
    list_display = ('id', 'invoice_number', 'customer', 'amount',
                    'gst', 'total_amount') + CoreModelAdmin.list_display
    search_fields = ('id', 'invoice_number', 'slug', 'customer__name', 'amount', 'gst', 'total_amount')
    raw_id_fields = ('customer', 'cart', )
    inlines = (InvoiceProductInline,)


admin.site.register(Invoice, InvoiceAdmin)


class CartProductInline(admin.TabularInline):
    model = CartProduct
    show_change_link = True
    extra = 0
    raw_id_fields = ('product', )


class CartAdmin(CoreModelAdmin):
    list_display = ('id', 'invoice_number', 'customer', 'amount',
                    'gst', 'total_amount', 'is_open',) + CoreModelAdmin.list_display
    search_fields = ('id', 'slug', 'invoice_number', 'slug', 'customer__name',
                     'amount', 'gst', 'total_amount',)
    raw_id_fields = ('customer', )
    inlines = (CartProductInline,)


admin.site.register(Cart, CartAdmin)


class InvoiceProductAdmin(CoreModelAdmin):
    list_display = ('id', 'invoice', 'product', 'amount',
                    'gst') + CoreModelAdmin.list_display
    search_fields = ('id', 'invoice__invoice_number', 'product__sku', 'amount', 'gst')
    raw_id_fields = ('invoice', 'product', )


admin.site.register(InvoiceProduct, InvoiceProductAdmin)


class CartProductAdmin(CoreModelAdmin):
    list_display = ('id', 'cart', 'product', 'amount',
                    'gst') + CoreModelAdmin.list_display
    search_fields = ('id', 'cart__invoice_number', 'product__sku', 'amount', 'gst')
    raw_id_fields = ('cart', 'product', )


admin.site.register(CartProduct, CartProductAdmin)


class PaymentAdmin(CoreModelAdmin):
    list_display = ('id', 'invoice', 'payment_date', 'is_processed', 'new_object_id', 'paid_amount', 'payment_mode',
                    'payment_source', 'source_reference', ) + CoreModelAdmin.list_display
    search_fields = ('id', 'slug', 'invoice__invoice_number', 'invoice__id', 'payment_date',
                     'is_processed', 'payment_mode', 'paid_amount', 'payment_source', 'source_reference',)
    raw_id_fields = ('invoice', 'customer',)


admin.site.register(Payment, PaymentAdmin)
