# Generated by Django 4.2 on 2023-04-13 09:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('toko', '0007_alamatpengiriman_order_alamat_pengiriman'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alamatpengiriman',
            options={'verbose_name_plural': 'AlamatPengiriman'},
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('payment_option', models.CharField(choices=[('P', 'Paypal'), ('S', 'Stripe')], max_length=1)),
                ('charge_id', models.CharField(max_length=50)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Payment',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='toko.payment'),
        ),
    ]