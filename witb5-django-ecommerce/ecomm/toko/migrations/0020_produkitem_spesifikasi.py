# Generated by Django 4.2 on 2023-06-04 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toko', '0019_remove_produkitem_spesifikasi'),
    ]

    operations = [
        migrations.AddField(
            model_name='produkitem',
            name='spesifikasi',
            field=models.TextField(default=False),
        ),
    ]
