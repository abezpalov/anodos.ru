# Generated by Django 3.2.7 on 2021-09-20 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distributors', '0026_party_party_search_idx'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendor',
            name='distributor',
        ),
    ]
