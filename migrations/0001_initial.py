# Generated by Django 3.2.9 on 2021-11-29 12:26

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtm_created', models.DateTimeField(auto_now_add=True, verbose_name='DTM Created')),
                ('dtm_updated', models.DateTimeField(auto_now=True, verbose_name='DTM Updated')),
                ('is_deleted', models.BooleanField(default=False)),
                ('address', models.TextField(blank=True, default=None, null=True)),
                ('city', models.CharField(blank=True, default=None, max_length=128, null=True)),
                ('state', models.CharField(blank=True, default=None, max_length=128, null=True)),
                ('pincode', models.CharField(blank=True, default=None, max_length=8, null=True)),
                ('country', models.CharField(blank=True, default=None, max_length=128, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtm_created', models.DateTimeField(auto_now_add=True, verbose_name='DTM Created')),
                ('dtm_updated', models.DateTimeField(auto_now=True, verbose_name='DTM Updated')),
                ('slug', models.SlugField(default=None, max_length=32, null=True, unique=True)),
                ('invoice_number', models.CharField(max_length=20, unique=True)),
                ('invoice_date', models.DateField(blank=True, default=None, null=True)),
                ('due_date', models.DateField(blank=True, default=None, null=True)),
                ('amount', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('gst', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('billing_address', models.TextField(blank=True, default=None, null=True)),
                ('shipping_address', models.TextField(blank=True, default=None, null=True)),
                ('is_open', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtm_created', models.DateTimeField(auto_now_add=True, verbose_name='DTM Created')),
                ('dtm_updated', models.DateTimeField(auto_now=True, verbose_name='DTM Updated')),
                ('slug', models.SlugField(default=None, max_length=32, null=True, unique=True)),
                ('name', models.CharField(blank=True, default=None, max_length=128, null=True, verbose_name='Company Name')),
                ('contact_name', models.CharField(blank=True, default=None, max_length=128, null=True)),
                ('phone', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('gstin', models.CharField(blank=True, default=None, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message='Enter valid GSTIN number. Up to 15 digits allowed.', regex='^[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9a-zA-Z]{1}Z|z[0-9a-zA-Z]{1}$')], verbose_name='GSTIN')),
                ('pan', models.CharField(blank=True, default=None, max_length=10, null=True, validators=[django.core.validators.RegexValidator(message='Enter valid PAN number. Up to 10 digits allowed.', regex='^[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}$')], verbose_name='PAN')),
                ('gstin_verified', models.BooleanField(default=False, verbose_name='GSTIN Verified')),
                ('pan_verified', models.BooleanField(default=False, verbose_name='PAN Verified')),
                ('website', models.URLField(blank=True, default=None, null=True)),
                ('whatsapp', models.CharField(blank=True, default=None, max_length=16, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?[1-9]\\d{4,14}$')], verbose_name='WhatsApp')),
                ('billing_address', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='billing_customers', to='payments.address')),
                ('primary_contact', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='primay_customer', to=settings.AUTH_USER_MODEL, verbose_name='Primary Contact')),
                ('shipping_address', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shipping_customers', to='payments.address')),
                ('users', models.ManyToManyField(blank=True, related_name='users_customers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtm_created', models.DateTimeField(auto_now_add=True, verbose_name='DTM Created')),
                ('dtm_updated', models.DateTimeField(auto_now=True, verbose_name='DTM Updated')),
                ('slug', models.SlugField(default=None, max_length=32, null=True, unique=True)),
                ('invoice_number', models.CharField(max_length=20, unique=True)),
                ('invoice_date', models.DateField(blank=True, default=None, null=True)),
                ('due_date', models.DateField(blank=True, default=None, null=True)),
                ('amount', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('gst', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('billing_address', models.TextField(blank=True, default=None, null=True)),
                ('shipping_address', models.TextField(blank=True, default=None, null=True)),
                ('cart', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='payments.cart')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='payments.customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtm_created', models.DateTimeField(auto_now_add=True, verbose_name='DTM Created')),
                ('dtm_updated', models.DateTimeField(auto_now=True, verbose_name='DTM Updated')),
                ('sku', models.CharField(max_length=8, unique=True)),
                ('amount', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('description', models.CharField(blank=True, default=None, max_length=128, null=True)),
                ('category', models.CharField(choices=[('plan', 'Plan'), ('feature', 'Feature'), ('minutes', 'Minutes'), ('messages', 'Messages'), ('custom', 'Custom')], max_length=16)),
                ('monthly_validity', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=False, verbose_name='Active')),
                ('expiry_date', models.DateField(blank=True, default=None, null=True, verbose_name='Expiry Date')),
                ('sac_code', models.CharField(blank=True, default=None, max_length=6, null=True)),
                ('addon', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons', to='payments.product')),
            ],
            options={
                'db_table': 'billing_product',
                'unique_together': {('amount', 'category', 'monthly_validity', 'is_active')},
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtm_created', models.DateTimeField(auto_now_add=True, verbose_name='DTM Created')),
                ('dtm_updated', models.DateTimeField(auto_now=True, verbose_name='DTM Updated')),
                ('slug', models.SlugField(default=None, max_length=32, null=True, unique=True)),
                ('payment_date', models.DateField(blank=True, default=None, null=True)),
                ('payment_mode', models.CharField(choices=[('Cash', 'Cash'), ('Bank Remittance', 'Bank Remittance'), ('Credit Card', 'Credit Card'), ('Debit Card', 'Debit Card'), ('Wallet', 'Wallet'), ('Online', 'Online')], max_length=16)),
                ('payment_source', models.CharField(blank=True, choices=[('GooglePay', 'GooglePay'), ('Swipez', 'Swipez'), ('Stripe', 'Stripe'), ('RazorPay', 'RazorPay'), ('Paytm', 'Paytm')], default=None, max_length=16, null=True)),
                ('paid_amount', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('source_reference', models.CharField(blank=True, default=None, max_length=32, null=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('new_object_id', models.CharField(blank=True, default=None, max_length=64, null=True)),
                ('post_dict', models.JSONField(blank=True, default=dict)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='payments.customer')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='payments.invoice')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InvoiceProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtm_created', models.DateTimeField(auto_now_add=True, verbose_name='DTM Created')),
                ('dtm_updated', models.DateTimeField(auto_now=True, verbose_name='DTM Updated')),
                ('qty', models.IntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('unit_gst', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('gst', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('sac_code', models.CharField(blank=True, default=None, max_length=6, null=True)),
                ('description', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('start_date', models.DateField(blank=True, default=None, null=True, verbose_name='Start Date')),
                ('end_date', models.DateField(blank=True, default=None, null=True, verbose_name='End Date')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='items', to='payments.invoice')),
                ('product', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='payments.product')),
            ],
            options={
                'verbose_name': 'Invoice Detail',
                'db_table': 'billing_invoice_ivr_product',
            },
        ),
        migrations.CreateModel(
            name='CartProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtm_created', models.DateTimeField(auto_now_add=True, verbose_name='DTM Created')),
                ('dtm_updated', models.DateTimeField(auto_now=True, verbose_name='DTM Updated')),
                ('qty', models.IntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('unit_gst', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('gst', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('sac_code', models.CharField(blank=True, default=None, max_length=6, null=True)),
                ('description', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('start_date', models.DateField(blank=True, default=None, null=True, verbose_name='Start Date')),
                ('end_date', models.DateField(blank=True, default=None, null=True, verbose_name='End Date')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='items', to='payments.cart')),
                ('product', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='payments.product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='cart',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='payments.customer'),
        ),
        migrations.AddConstraint(
            model_name='cart',
            constraint=models.UniqueConstraint(condition=models.Q(('is_open', True)), fields=('customer',), name='unique_customer_is_open'),
        ),
    ]
