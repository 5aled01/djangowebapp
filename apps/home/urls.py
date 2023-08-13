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

    path('change_balance', views.change_balance, name='change_balance'),

    path('free_invoice_save', views.free_invoice_save, name='free_invoice_save'),

    

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

    path('delete_free_invoice', views.delete_free_invoice, name='delete_free_invoice'),

    path('cencel_transanction', views.cencel_transanction, name='cencel_transanction'),
    path('cancel_transanction_balance', views.cancel_transanction_balance, name='cancel_transanction_balance'),
    path('cencel_freetransanction', views.cencel_freetransanction, name='cencel_freetransanction'),

    path('generate_transaction_pdf', views.generate_transaction_pdf, name='generate_transaction_pdf'),

    path('generate_free_pdf', views.generate_free_pdf, name='generate_free_pdf'),

    path('change_invoice_status', views.change_invoice_status, name='change_invoice_status'),
    path('change_free_invoice_status', views.change_free_invoice_status, name='change_free_invoice_status'),

    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),

    path('health/',views.health_check, name='health_check'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
if settings.DEBUG:  # new
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
