# Generated by Django 3.2.6 on 2023-08-13 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_auto_20230805_2344'),
    ]

    operations = [
        migrations.CreateModel(
            name='FreeInvoiceImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_data', models.BinaryField()),
                ('FreeInvoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.freeinvoice')),
            ],
        ),
    ]
