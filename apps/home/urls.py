# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    # Customer detail page
    path('customers_detail/<int:customer_id>/', views.customer_detail, name='customer_detail'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
