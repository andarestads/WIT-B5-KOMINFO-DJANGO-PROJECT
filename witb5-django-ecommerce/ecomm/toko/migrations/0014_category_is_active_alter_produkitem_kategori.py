# Generated by Django 4.2 on 2023-06-03 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toko', '0013_rename_nama_kategori_category_nama_produk'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='produkitem',
            name='kategori',
            field=models.CharField(choices=[('LE', 'Low-End'), ('MR', 'Mid-Range'), ('FS', 'Flagship')], max_length=2),
        ),
    ]
