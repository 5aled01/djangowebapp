# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.utils import timezone
from django import template
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Sum

from .forms import CustomerForm, ContainerForm
from .models import Customer, Container
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.postgres.search import SearchVector
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
from django.template import loader
from django.urls import reverse
from .models import Customer

from django.http import JsonResponse
import json
from .models import Invoice, Item
from django.utils.crypto import get_random_string

from django.shortcuts import render

context = {}


@login_required(login_url="/login/")
def index(request):

    customer_count = Customer.objects.count()
    total_income= Item.objects.aggregate(total=Sum('price'))['total']
    total_expences= Container.objects.aggregate(total=Sum('price'))['total']

    three_days_ago = timezone.now() - timedelta(days=3)

    new_customer_count = Customer.objects.filter(created_date__gte=three_days_ago).count()

    sum_of_prices = Item.objects.filter(created_date__gte=three_days_ago).aggregate(total_price=Sum('price'))['total_price']
    sum_of_expences = Container.objects.filter(created_date__gte=three_days_ago).aggregate(total_price=Sum('price'))['total_price']


    if sum_of_prices is None:
        sum_of_prices = 0
    
    if sum_of_expences is None:
        sum_of_expences = 0
    
    if new_customer_count is None:
        new_customer_count = 0
    
    # Calculate the percentage
    if new_customer_count > 0 and customer_count > 0:
        percentage_customer = (new_customer_count / customer_count) * 100
    else:
        percentage_customer = 0

    if sum_of_prices > 0 and total_income > 0:
        percentage_income = (sum_of_prices / total_income) * 100
    else:
        percentage_income = 0
    
    if sum_of_expences > 0 and total_expences > 0:
        percentage_expences = (sum_of_expences / total_expences) * 100
    else:
        percentage_expences = 0

    context = {'segment': 'index',
               'customer_count': customer_count,
                'percentage_customer': percentage_customer, 
                'total_income': total_income,
                'percentage_income': percentage_income,
                'total_expences': total_expences,
                'percentage_expences': percentage_expences,
                
                }

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

                customers = Customer.objects.annotate(search=SearchVector(
                    'name', 'phone_number', 'brand', 'partner')).filter(search=search_query)

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

        if load_template == 'container_detail.html':
            container_id = request.GET.get('container_id')
            container = get_object_or_404(Container, id=container_id)
            context['container'] = container

            invoices = container.invoice.all()
            invoice_summaries = []

            total_quantity = 0
            total_cbm = 0
            total_price = 0
            
            for invoice in invoices:
                # Get all items related to the invoice
                items = invoice.items.all()
                invoice_summary = {
                    'customer_name': invoice.customer.name,
                    'total_quantity': items.aggregate(Sum('quantity'))['quantity__sum'],
                    'total_cbm': items.aggregate(Sum('CBM'))['CBM__sum'],
                    'total_price': items.aggregate(Sum('price'))['price__sum']
                 }
                

                # Calculate and add the quantities, CBM, and price for each item
                invoice_summaries.append(invoice_summary)

                total_quantity += invoice_summary['total_quantity'] or 0
                total_cbm += invoice_summary['total_cbm'] or 0
                total_price += invoice_summary['total_price'] or 0
            
            context['invoice_summaries'] = invoice_summaries
            context['total_quantity'] = total_quantity
            context['total_cbm'] = total_cbm
            context['total_price'] = total_price

            return render(request, 'home/container_detail.html', context)
        

        if load_template == 'invoices_detail.html':
            customer_id = request.GET.get('customer_id')
            customer = get_object_or_404(Customer, id=customer_id)
            context['customer'] = customer

        if load_template == 'containers.html':
            search_query = request.GET.get('search', '')

            if search_query != '':

                containers = Container.objects.annotate(search=SearchVector(
                    'id', 'created_date', 'size', 'status')).filter(search=search_query)

            else:
                containers = Container.objects.all()

            paginator = Paginator(containers, per_page=4)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['containers'] = page_obj

        print('load_template----', load_template)

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
    customer_id = request.GET.get('customer_id')
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)

        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated successfully.")
            return redirect('customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)

    context = {'form': form, 'customer': customer}
    return render(request, 'home/customer_detail.html', context)


@login_required(login_url="/login/")
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    form = CustomerForm(instance=customer)
    context = {'form': form, 'customer': customer}
    return render(request, 'home/customer_detail.html', context)

@login_required(login_url="/login/")
def container_detail(request, container_id):
    container = get_object_or_404(Container, id=container_id)
    context = {'container': container}
    return render(request, 'home/container_detail.html', context)


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



@login_required(login_url="/login/")
def add_container(request):
    if request.method == 'POST':
        form = ContainerForm(request.POST)
        
        if form.is_valid():
            container = form.save(commit=False)
            container.created_date = datetime.now()
            container.save()
            
            messages.success(request, "Container added successfully.")
            return redirect('home/containers.html')
    else:
        form = ContainerForm()

    containers = Container.objects.all()
    context = {'form': form, 'containers': containers}
    return render(request, 'home/containers.html', context)


def delete_customer(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        customer.delete()
        messages.success(request, "Customer deleted successfully.")
        # Redirect to the desired URL after successful deletion
        return redirect('customers.html')

def delete_container(request):
    if request.method == 'POST':
        container_id = request.POST.get('container_id')
        container = get_object_or_404(Container, id=container_id)
        container.delete()
        messages.success(request, "Container deleted successfully.")
        # Redirect to the desired URL after successful deletion
        return redirect('containers.html')


@login_required(login_url="/login/")
def invoices_detail(request):

    try:
        customer_id = request.GET.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        context['customer'] = customer

        print('customer_id----', customer_id)

        return render(request, 'invoices_detail.html', context)

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


def generate_invoice_id():
    timestamp = timezone.now().strftime("%y%m%d%H%M%S")
    random_string = get_random_string(
        length=7, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    return f"MRSU{timestamp}{random_string}"


def Invoice_save(request):
    if request.method == "POST":
        invoice_items = json.loads(request.body)
        totalprice = 0
        totalcbm = 0
        totalpack = 0
        customer = None
        items = []

        customer = Customer.objects.get(id=invoice_items[0]["id_customer"])
        invoice = Invoice(customer=customer)
        invoice.save()  # Save the invoice to obtain the ID
        
        for item in invoice_items:
            
            item_obj = Item(
                invoice=invoice,
                item=item["item"],
                quantity=item["quantity"],
                length=item["length"],
                width=item["width"],
                height=item["height"],
                CBM=item["CBM"],
                rate=item["rate"],
                price=item["price"]
            )
            item_obj.save()

            items.append(item_obj)

            totalprice += item["price"]
            totalcbm += item["CBM"]
            totalpack += item["quantity"]

            #add create message
            container, create = Container.objects.get_or_create(id=item["manifest"])
            print('----------->',container)
            container.invoice.add(invoice)
            container.save()


            #print('not goood------')
            #messages.success(request, "Id manifest does not exist.")
            #load_template = 'invoices_detail.html'
            #html_template = loader.get_template('home/' + load_template)
            #return HttpResponse(html_template.render(context, request))
            


        context['totalprice'] = totalprice
        context['totalcbm'] = totalcbm
        context['totalpack'] = totalpack

        context['customer'] = customer
        context['invoice'] = invoice
        context['items'] = items


        load_template = 'final_invoice.html'
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    else:
        return JsonResponse({"error": "Invalid request method"})
