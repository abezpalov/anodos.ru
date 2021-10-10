# Generated by Django 3.2.7 on 2021-10-10 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pflops', '0006_product_slug'),
        ('distributors', '0047_alter_parameter_to_pflops'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterunit',
            name='to_pflops',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='pflops.unit'),
        ),
    ]
