# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from .forms import CustomerForm
from .models import Customer
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.postgres.search import SearchVector


from django.template import loader
from django.urls import reverse

from .models import Customer
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
        
        context['customer'] = customer

        form = CustomerForm(request.POST, instance=customer)
        
        print(form)
        if form.is_valid():
            form.save()
            messages.success(request, "Password updated successfully.")
            html_template = loader.get_template('home/customer_detail.html')
            return HttpResponse(html_template.render(context, request))  # Redirect to the customer list page after successful submission
    else: 
        form = CustomerForm(instance=customer)
    html_template = loader.get_template('home/customer_detail.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()

            print('add_customer ----------', form)
            messages.success(request, "Customer added successfully.")
            return redirect('home/customers.html')  # Redirect to the customer list page after successful submission
    else:
        form = CustomerForm()

    customers = Customer.objects.all()
    context = {'form': form, 'customers': customers}
    return render(request, 'home/customers.html', context)



@login_required(login_url="/login/")
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        return redirect('home/customer_detail.html')  # Redirect to the customer list page after successful deletion

    return render(request, 'customer_detail.html', {'customer': customer})



@login_required(login_url="/login/")
def customer_detail(request):

    try:

        customer_id = request.GET.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        context['customer'] = customer
            
            #print('load_template----', load_template)

        return render(request, 'customer_detail.html', {'customer': customer})

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

