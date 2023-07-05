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
    path('customer_detail', views.customer_detail, name='customer_detail'),
    path('add_customer', views.add_customer, name='add_customer'),
    path('delete_customer', views.delete_customer, name='delete_customer'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

    
]
