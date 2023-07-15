from django.db import models
import uuid
from django.utils import timezone

class Customer(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    brand = models.CharField(max_length=100)
    partner = models.CharField(max_length=100, default='Gemal')
    created_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id or not self.pk:
            self.id = 'CUST' + str(uuid.uuid4().fields[-1])[:6]
        super().save(*args, **kwargs)

class Container(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    invoice = models.ManyToManyField('Invoice', related_name='containers')
    created_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100, default='Just Created')
    size = models.IntegerField(default=20)
    price = models.IntegerField(default=20)

    def save(self, *args, **kwargs):
        if not self.id or not self.pk:
            self.id = 'MRSU' + str(uuid.uuid4().fields[-1])[:6]
        super().save(*args, **kwargs)


class Invoice(models.Model):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id or not self.pk:
            self.id = 'INVO' + str(uuid.uuid4().fields[-1])[:6]
        super().save(*args, **kwargs)

class Item(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item = models.CharField(max_length=100)
    quantity = models.IntegerField()
    length = models.DecimalField(max_digits=10, decimal_places=2)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    CBM = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    created_date = models.DateTimeField(default=timezone.now)

class InvoiceImage(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="invoice_images/")

    def __str__(self):
        return f"Image for Invoice #{self.invoice.id}"