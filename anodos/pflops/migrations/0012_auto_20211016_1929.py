# Generated by Django 3.2.7 on 2021-10-16 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pflops', '0011_auto_20211016_1924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='quantity',
            field=models.FloatField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='currency',
            name='rate',
            field=models.FloatField(default=None, null=True),
        ),
    ]
