# Generated by Django 3.0.3 on 2020-04-28 16:39

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
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
        migrations.CreateModel(
            name='SourceData',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('url', models.TextField(db_index=True, default=None, null=True)),
                ('file_name', models.TextField(default=None, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('parsed', models.DateTimeField(default=None, null=True)),
                ('source', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='swarm.Source')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file_name', models.TextField(default=None, null=True)),
                ('content', models.TextField(default=None, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('source_data', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='swarm.SourceData')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
    ]
