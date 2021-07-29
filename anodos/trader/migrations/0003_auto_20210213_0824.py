# Generated by Django 3.0.6 on 2021-02-13 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0002_auto_20210213_0806'),
    ]

    operations = [
        migrations.AddField(
            model_name='instrument',
            name='minPriceIncrement',
            field=models.DecimalField(decimal_places=10, default=None, max_digits=19, null=True),
        ),
        migrations.AlterField(
            model_name='instrument',
            name='isin',
            field=models.CharField(default=None, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='instrument',
            name='lot',
            field=models.BigIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='instrument',
            name='ticker',
            field=models.CharField(default=None, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='instrument',
            name='type',
            field=models.CharField(default=None, max_length=128, null=True),
        ),
    ]