# Generated by Django 3.2.6 on 2023-07-19 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_rename_image_invoiceimage_image_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='source',
            field=models.CharField(default='Supplier A', max_length=100),
        ),
    ]
