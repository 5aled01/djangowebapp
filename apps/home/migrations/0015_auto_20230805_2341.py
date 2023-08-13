# Generated by Django 3.2.6 on 2023-08-05 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_freetransaction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='freetransaction',
            name='rest',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='rest',
        ),
        migrations.AddField(
            model_name='freetransaction',
            name='paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='transaction',
            name='paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]