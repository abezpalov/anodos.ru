# Generated by Django 3.2.5 on 2021-08-24 19:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distributors', '0002_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='article',
        ),
    ]