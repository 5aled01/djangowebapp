# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
import django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from faker import Faker
from .forms import CustomerForm
from .models import Customer
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.postgres.search import SearchVector
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
from .forms import InvoiceForm
from django.template import loader
from django.urls import reverse
from .models import Customer

import io
from django.http import FileResponse
from django.shortcuts import render
from faker import Faker
from reportlab.lib.units import inch 
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
context = {}


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        
        if load_template == 'customers.html':
            search_query = request.GET.get('search', '')
            
            if search_query != '':
                
                customers = Customer.objects.annotate(search=SearchVector('name', 'phone_number', 'brand', 'partner')).filter(search=search_query)
            
            else:
                customers = Customer.objects.all()
                
            paginator = Paginator(customers, per_page=4)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['customers'] = page_obj

        if load_template == 'customer_detail.html':
                customer_id = request.GET.get('customer_id')
                customer = get_object_or_404(Customer, id=customer_id)
                context['customer'] = customer
        
        #print('load_template----', load_template)

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def edit_customer(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        form = CustomerForm(request.POST, instance=customer)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated successfully.")
            return redirect('customers.html', customer_id=customer_id)
    else:
        customer_id = request.GET.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        form = CustomerForm(instance=customer)
    
    context = {'form': form, 'customer': customer}
    return render(request, 'home/customer_detail.html', context)

@login_required(login_url="/login/")
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_date = datetime.now()
            customer.save()
            messages.success(request, "Customer added successfully.")
            return redirect('home/customers.html')
    else:
        form = CustomerForm()

    customers = Customer.objects.all()
    context = {'form': form, 'customers': customers}
    return render(request, 'home/customers.html', context)

def index(request):
    customer_count = Customer.objects.count()
    return render(request, 'home/index.html', {'customer_count': customer_count})

def dashboard(request):
    customer_count = Customer.objects.count()
    
    # Calculate the number of customers created within the last 3 days or more
    today = timezone.now().date()
    three_days_ago = today - timedelta(days=3)
    new_customer_count = Customer.objects.filter(created_date__lt=three_days_ago).count()

    # Calculate the percentage
    if customer_count > 0:
        percentage = (new_customer_count / customer_count) * 100
    else:
        percentage = 0
    
    return render(request, 'home/index.html',9)

def delete_customer(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        customer.delete()
        messages.success(request, "Customer deleted successfully.")
        return redirect('customers.html')  # Redirect to the desired URL after successful deletion



@login_required(login_url="/login/")
def invoices_detail(request):

    try:
        customer_id = request.GET.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        context['customer'] = customer
            
        print('customer_id----', customer_id)

        return render(request, 'invoices_detail.html', {'customer': customer})

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

def Invoice_save(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            instance = form.save()  # Save the form data to the database
            return redirect('success')  # Redirect to a success page or another view
    else:
        form = InvoiceForm(initial={'field_name': 'default_value'})  # Set initial values for the form fields

    return render(request, 'your_template.html', {'form': form})






def generate_invoice_pdf(request):
    fake = Faker()

    # Generate fake data
    data = []
    for _ in range(10):
        data.append({
            'id': fake.random_int(min=1000, max=9999),
            'id_customer': fake.random_int(min=1000, max=9999),
            'date': fake.date(),
            'item': fake.word(),
            'quantity': fake.random_int(min=1, max=10),
            'length': fake.random_int(min=10, max=100),
            'width': fake.random_int(min=10, max=100),
            'height': fake.random_int(min=10, max=100),
            'CBM': fake.random_int(min=10, max=100),
            'rate': fake.random_int(min=10, max=100),
            'price': fake.random_int(min=10, max=100),
            'total_cbm': fake.random_int(min=10, max=100),
            'total': fake.random_int(min=100, max=1000),
        })

    # Create a PDF document
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    # Create text object
    text_y = 750
    for d in data:
        c.drawString(100, text_y, f"Item: {d['item']}")
        c.drawString(200, text_y, f"Quantity: {d['quantity']}")
        c.drawString(300, text_y, f"Price: {d['price']}")
        text_y -= 20

    # Finish up
    c.showPage()
    c.save()
    buf.seek(0)

    # Return the generated PDF as a response
    return FileResponse(buf, as_attachment=True, filename='Invoice.pdf')


    
