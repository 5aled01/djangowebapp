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
from django.contrib import messages

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
            customers = Customer.objects.all()
            context['customers'] = customers

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


def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        return redirect('home/customer_detail.html')  # Redirect to the customer list page after successful deletion

    return render(request, 'customer_detail.html', {'customer': customer})



