# Generated by Django 3.0.6 on 2021-02-13 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrument',
            name='ticker',
            field=models.CharField(default=None, max_length=128),
        ),
    ]