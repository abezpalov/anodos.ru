# Generated by Django 3.0.3 on 2020-04-19 17:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=512, unique=True)),
                ('login', models.TextField(default=None, null=True)),
                ('password', models.TextField(default=None, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
