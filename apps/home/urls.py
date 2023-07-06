# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import generate_invoice_pdf

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    path('edit_customer', views.edit_customer, name='edit_customer'),
    path('invoices_detail', views.invoices_detail, name='invoices_detail'),
    path('add_customer', views.add_customer, name='add_customer'),
    path('delete_customer', views.delete_customer, name='delete_customer'),
    path('index', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('Invoice_save', views.Invoice_save, name='Invoice_save'),
    path('generate-invoice-pdf', generate_invoice_pdf, name='generate_invoice_pdf'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

    
]
