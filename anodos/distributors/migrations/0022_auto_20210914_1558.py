# Generated by Django 3.2.7 on 2021-09-14 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distributors', '0021_auto_20210912_2006'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['vendor__name', 'part_number']},
        ),
        migrations.RenameField(
            model_name='category',
            old_name='article',
            new_name='key',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='article',
            new_name='part_number',
        ),
    ]
