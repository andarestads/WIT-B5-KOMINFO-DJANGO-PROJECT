# Generated by Django 4.2 on 2023-06-03 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toko', '0014_category_is_active_alter_produkitem_kategori'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='is_active',
        ),
    ]
