# Generated by Django 3.2.7 on 2021-09-26 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributors', '0034_vendor_distributor'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='gtin',
            field=models.TextField(db_index=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='outoftrade',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='promo',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]