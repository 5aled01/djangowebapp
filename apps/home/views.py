# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from .models import Customer

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        customers = Customer.objects.all()
        #print('-------', customers )
        context['customers'] = customers

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        if load_template == 'customers':
            customers = Customer.objects.all()
            #print('-------', customers )
            context['customers'] = customers
        
        if load_template == 'customer_detail':
            print('----------------test00')

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def customer_detail(request, customer_id):
    print('----------------test01')
    customer = get_object_or_404(Customer, id=customer_id)
    print('----------------test20')
    context = {'customer': customer}
    return render(request, 'home/customer_detail.html', context)
