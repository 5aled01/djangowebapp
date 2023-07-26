# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.conf.urls.static import static
from django.urls import path, re_path, include
from apps.home import views
from core import settings
from wkhtmltopdf.views import PDFTemplateView


urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    path('edit_customer', views.edit_customer, name='edit_customer'),
    path('customer_detail/<customer_id>/', views.customer_detail, name='customer_detail'),

    path('delete_container', views.delete_container, name='delete_container'),


    path('invoices_detail', views.invoices_detail, name='invoices_detail'),

    path('add_customer', views.add_customer, name='add_customer'),
    path('delete_customer', views.delete_customer, name='delete_customer'),


    path('add_container', views.add_container, name='add_container'),

    path('invoices_detail', views.invoices_detail, name='invoices_detail'),
    path('invoice_save', views.Invoice_save, name='invoice_save'),
    path('invoices', views.invoices, name='invoices'),
    path('save_images', views.save_images, name='save_images'),
    path('get_invoice_images', views.get_invoice_images, name='get_invoice_images'),
    path('delete_invoice', views.delete_invoice, name='delete_invoice'),

    path('change_invoice_status', views.change_invoice_status, name='change_invoice_status'),

    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
if settings.DEBUG:  # new
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
