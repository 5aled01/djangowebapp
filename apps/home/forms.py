"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from .models import Customer, Invoice, Item, Container



class CustomerForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "name",
                "class": "form-control"
            }
        ))
    phone_number = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                "placeholder": "phone_number",
                "class": "form-control"
            }
        ))

    brand = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Brand",
                "class": "form-control"
            }
        ))


    partner = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Partner",
                "class": "form-control"
            }
        ))

    class Meta:
        model = Customer
        fields = ('name', 'phone_number', 'brand', 'partner')



class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('invoice', 'item', 'quantity', 'length', 'width', 'height', 'CBM', 'rate', 'price')

class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ('id', 'size', 'manifaist')