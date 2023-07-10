# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from .models import Customer
from .models import Invoice



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

    partner = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Password brand",
                "class": "form-control"
            }
        ))


    partner = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Password partner",
                "class": "form-control"
            }
        ))

    class Meta:
        model = Customer
        fields = ('name', 'phone_number', 'brand', 'partner')



class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['id_customer', 'date', 'item', 'quantity', 'length', 'width', 'height', 'CBM', 'rate', 'price']

    total_cbm = forms.DecimalField(disabled=True, required=False)
    total = forms.DecimalField(disabled=True, required=False)




class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('invoice', 'item', 'quantity', 'length', 'width', 'height', 'CBM', 'rate', 'price')

class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ('id', 'size', 'price')