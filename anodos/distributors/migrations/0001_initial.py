# Generated by Django 3.2.5 on 2021-08-24 16:43

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Distributor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=512, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]