# Generated by Django 3.0.6 on 2021-03-22 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0006_candle'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='candle',
            options={'ordering': ['-datetime']},
        ),
        migrations.AlterField(
            model_name='candle',
            name='v',
            field=models.BigIntegerField(),
        ),
    ]
