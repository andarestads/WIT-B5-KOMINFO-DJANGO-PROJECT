# Generated by Django 4.2 on 2023-06-03 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toko', '0016_category_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='produkitem',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
