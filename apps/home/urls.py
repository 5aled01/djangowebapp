# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    path('edit_customer', views.edit_customer, name='edit_customer'),
    path('customer_detail/<uuid:customer_id>/', views.customer_detail, name='customer_detail'),
    
    path('container_detail/<container_id>/', views.container_detail, name='container_detail'),
    path('delete_container', views.delete_container, name='delete_container'),


    path('invoices_detail', views.invoices_detail, name='invoices_detail'),
    path('invoices_affiche', views.invoices_affiche, name='invoices_affiche'),

    path('add_customer', views.add_customer, name='add_customer'),
    path('delete_customer', views.delete_customer, name='delete_customer'),


    path('invoices_detail', views.invoices_detail, name='invoices_detail'),
    path('invoice_save', views.Invoice_save, name='invoice_save'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

    
]
