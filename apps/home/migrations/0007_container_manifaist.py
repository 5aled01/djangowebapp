# Generated by Django 3.2.6 on 2023-07-25 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_item_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='container',
            name='manifaist',
            field=models.IntegerField(default=20),
        ),
    ]
