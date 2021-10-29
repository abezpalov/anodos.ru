# Generated by Django 3.2.7 on 2021-10-27 18:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('pflops', '0018_auto_20211027_1620'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.TextField(db_index=True)),
                ('slug', models.TextField(db_index=True, default=None, null=True)),
                ('path', models.TextField(db_index=True, default=None, null=True)),
                ('content', models.TextField(default=None, null=True)),
                ('description', models.TextField(default=None, null=True)),
                ('assistant', models.BooleanField(db_index=True, default=False)),
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('edited', models.DateTimeField(db_index=True, default=None, null=True)),
                ('published', models.DateTimeField(db_index=True, default=None, null=True)),
                ('image', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='pflops.image')),
                ('parent', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='pflops.catalogelement')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]