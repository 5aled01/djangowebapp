# Generated by Django 3.2.6 on 2023-07-17 21:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20230717_2238'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invoiceimage',
            old_name='image',
            new_name='image_data',
        ),
    ]