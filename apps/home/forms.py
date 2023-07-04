# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from .models import Customer



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



