# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""


# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import PyPDF2

import base64
from django import template
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
#from django.views.decorators.csrf import csrf_protect
import plotly.graph_objects as go
import plotly.io as pio
from .forms import CustomerForm, ContainerForm

import uuid
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.postgres.search import SearchVector
from datetime import datetime, timedelta
from django.utils import timezone
from django.template import loader
from django.urls import reverse
from django.db.models import Sum, Q
import json
from django.utils.crypto import get_random_string
from .models import Customer, Container, FreeInvoice, FreeItem, FreeTransaction, InvoiceImage, Item, Invoice, Transaction, CustomerTransaction



from xhtml2pdf import pisa
from io import StringIO, BytesIO
from django.template.loader import get_template 
from django.template import Context


context = {}

@login_required(login_url="/login/")
def index(request):

    #invoice_ids_to_update = ['INVO174400', 'INVO212087', 'INVO178535', 'INVO216389', 'INVO827928','INVO146189', 'INVO176014', 'INVO213283', 'INVO175456', 'INVO563290', 'INVO272650' ]
    #items_to_update = Item.objects.filter(invoice__id__in=invoice_ids_to_update)
    #items_to_update.update(rate=560.0)

    #Item.objects.all().update(rate=650.0)
    customer_count = Customer.objects.count()
    total_income = Transaction.objects.aggregate(total_income=Sum('amount'))['total_income'] or 0
    total_expenses = Container.objects.aggregate(total=Sum('price'))['total'] or 0

    three_days_ago = timezone.now() - timedelta(days=3)

    new_customer_count = Customer.objects.filter(created_date__gte=three_days_ago).count()

    sum_of_prices = Transaction.objects.filter(date__gte=three_days_ago).aggregate(total_price=Sum('amount'))['total_price'] or 0
    sum_of_expenses = Container.objects.filter(created_date__gte=three_days_ago).aggregate(total_price=Sum('price'))['total_price'] or 0

    # Calculate the percentage
    percentage_customer = (new_customer_count / customer_count) * 100 if customer_count > 0 else 0
    percentage_income = (sum_of_prices / total_income) * 100 if total_income > 0 else 0
    percentage_expenses = (sum_of_expenses / total_expenses) * 100 if total_expenses > 0 else 0

    items = Item.objects.all()
    context = {
        'segment': 'index',
        'customer_count': customer_count,
        'percentage_customer': percentage_customer,
        'total_income': total_income,
        'percentage_income': percentage_income,
        'total_expenses': total_expenses,
        'percentage_expenses': percentage_expenses,
        'items': items
    }

    # Extract the required data for the chart
    #dates = [item.created_date for item in items]
    #prices = [item.price for item in items]

    # Create a line chart
    #fig = go.Figure(data=go.Scatter(x=dates, y=prices, mode='lines'))

    # Disable plot options
    #fig.update_layout(
    #    showlegend=False,
    #    xaxis=dict(showgrid=False),
    #    yaxis=dict(showgrid=False),
    #    plot_bgcolor='#F8F9FE',  # Set the background color (transparent)
    #    paper_bgcolor='#F8F9FE',  # Set the paper color (transparent)
    #)

    #fig.update_layout(showlegend=False)

    # Convert the chart to HTML
    #chart_html = pio.to_html(fig)

    #context['chart_html'] = chart_html

    return render(request, 'home/index.html', context)



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

            paginator = Paginator(customers, per_page=20)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['customers'] = page_obj

        if load_template == 'customer_detail.html':
            request.session['delete_invoice_from_page'] = 'customer_detail'

            try:
                customer_id = request.GET.get('customer_id')
                customer = get_object_or_404(Customer, id=customer_id)
            except:
                customer_id = context['customer_id']
                customer = get_object_or_404(Customer, id=customer_id)

            #customer = get_object_or_404(Customer, id=customer_id)
            context['customer'] = customer

            print('customer', customer)

            context['customer_transaction'] = customer.customer_transactions.all()

            print('=======-=======')

            print(context['customer_transaction'])

            print('=======-=======')

            invoices = customer.invoices.all()
            freeinvoices = customer.freeinvoices.all()
            invoice_summaries = []
            free_invoice_summaries = []

            total_quantity = 0
            free_total_quantity = 0
            total_cbm = 0
            total_price  = 0
            free_total_price = 0
            total_debit = 0 
            free_total_debit = 0
            total_credit = 0
            free_total_credit = 0
            container_id = 0
            container_manifaist = 0
            free_total_rate = 0

            for freeinvoice in freeinvoices:


                # Get all items related to the invoice
                #items = invoice.items.all()
                #print('items =======-======= ', items)

                freeitems = freeinvoice.freeitems.all()

                print('freeitems', freeitems)

                if freeinvoice.status != 'Unpaid':
                    freetransaction = get_object_or_404(FreeTransaction, invoice=freeinvoice)
                else: 
                    freetransaction = 'noTransaction'
                
                free_invoice_summarie = {
                'invoice_id': freeinvoice.id,
                'transaction': freetransaction,
                'transaction_date': freetransaction.date if freeinvoice.status != 'Unpaid' else datetime.min,
                'status': freeinvoice.status,
                'customer_name': freeinvoice.customer.name,
                'total_quantity': freeitems.aggregate(Sum('quantity'))['quantity__sum'],
                'total_rate': freeitems.aggregate(Sum('rate'))['rate__sum'],
                'total_price': freeitems.aggregate(Sum('price'))['price__sum']
            }
                

                if freeinvoice.status == 'Paid':
                    if freetransaction.transaction_type == 'debit': 
                        free_total_debit += freetransaction.amount or 0
                    else:
                        free_total_credit += freetransaction.amount or 0


                free_total_quantity += free_invoice_summarie['total_quantity'] or 0
                free_total_rate += free_invoice_summarie['total_rate'] or 0
                free_total_price += free_invoice_summarie['total_price'] or 0
                free_invoice_summaries.append(free_invoice_summarie)

            for invoice in invoices:

                # Get all items related to the invoice
                items = invoice.items.all()


                if invoice.status != 'Unpaid':
                    transaction = get_object_or_404(Transaction, invoice=invoice)
                else: 
                    transaction = 'noTransaction'

                try:
                    container_for_invoice = invoice.containers.get()
                    print("Container ID:", container_for_invoice.id)

                    container_id = container_for_invoice.id
                    container_manifaist = container_for_invoice.manifaist

                except Container.DoesNotExist:
                    print("No container found for the given invoice.")

                except Container.MultipleObjectsReturned:
                    print("Multiple containers found for the given invoice.")

                # Assuming you have an invoice instance named 'invoice'


                invoice_summary = {
                'invoice_id': invoice.id,
                'transaction': transaction,
                'transaction_date': transaction.date if invoice.status != 'Unpaid' else datetime.min,
                'status': invoice.status,
                'container_id': container_id,
                'container_manifaist': container_manifaist,
                'customer_name': invoice.customer.name,
                'total_quantity': items.aggregate(Sum('quantity'))['quantity__sum'],
                'total_cbm': items.aggregate(Sum('CBM'))['CBM__sum'],
                'total_price': items.aggregate(Sum('price'))['price__sum']
            }
                
                # Calculate and add the quantities, CBM, and price for each item

                if invoice.status == 'Paid':
                    if transaction.transaction_type == 'debit': 
                        total_debit += transaction.amount or 0
                    else:
                        total_credit += transaction.amount or 0
                print('ok')        

                total_quantity += invoice_summary['total_quantity'] or 0
                total_cbm += invoice_summary['total_cbm'] or 0
                total_price += invoice_summary['total_price'] or 0
                invoice_summaries.append(invoice_summary)



            #invoice_summaries = sorted(invoice_summaries, key=lambda x: x['transaction_date'], reverse=True)
            invoice_summaries = sorted(invoice_summaries, key=lambda x: x['container_manifaist'])

            context['invoice_summaries'] = invoice_summaries
            context['free_invoice_summaries'] = free_invoice_summaries

            context['total_debit'] = total_debit
            context['total_credit'] = total_credit
            context['total_quantity'] = total_quantity
            context['total_cbm'] = total_cbm
            context['total_price'] = total_price

            context['free_total_debit'] = free_total_debit
            context['free_total_credit'] = free_total_credit
            context['free_total_quantity'] = free_total_quantity
            context['free_total_cbm'] = free_total_rate
            context['free_total_price'] = free_total_price

        if request.path == '/free_invoice/invoice_view.html':
            invoice_id = request.GET.get('invoice_id')
            invoice = get_object_or_404(FreeInvoice, id=invoice_id)

            #invoice_summaries = []
            
            load_template = '/free_invoice/invoice_view.html'

            total_quantity = 0
            total_price = 0
            # Get all items related to the invoice
            items = invoice.freeitems.all()

            #context['invoice_summaries'] = invoice_summaries
            context['invoice'] = invoice
            context['customer'] = invoice.customer
            context['items'] = items 
            context['totalpack'] = items.aggregate(s=Sum("quantity"))["s"]
            context['totalprice'] = items.aggregate(s=Sum("price"))["s"]

        if load_template == 'invoice_view.html':
            invoice_id = request.GET.get('invoice_id')
            invoice = get_object_or_404(Invoice, id=invoice_id)

            #invoice_summaries = []

            total_quantity = 0
            total_cbm = 0
            total_price = 0
            print('----', invoice.id)
            # Get all items related to the invoice
            items = invoice.items.all()
         
            #context['invoice_summaries'] = invoice_summaries
            context['invoice'] = invoice
            context['customer'] = invoice.customer
            context['items'] = items 
            context['totalpack'] = items.aggregate(s=Sum("quantity"))["s"]
            context['totalcbm'] = items.aggregate(s=Sum("CBM"))["s"]
            context['totalprice'] = items.aggregate(s=Sum("price"))["s"]

            context['new_balance'] = invoice.customer.balance - items.aggregate(s=Sum("price"))["s"]

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
        
        if load_template == 'containers.html':
            search_query = request.GET.get('search', '')

            if search_query != '':

                containers = Container.objects.annotate(search=SearchVector(
                    'id', 'created_date', 'size', 'status')).filter(search=search_query).order_by('-created_date')

            else:
                containers = Container.objects.all().order_by('-created_date')

            paginator = Paginator(containers, per_page=20)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['containers'] = page_obj

        if load_template == 'invoices.html':
                search_query = request.GET.get('search', '')
                request.session['delete_invoice_from_page'] = 'invoices'

                invoices = Invoice.objects.annotate(total_price=Sum('items__price')).values('id', 'customer_id', 'total_price', 'date').order_by('-date')

                if search_query != '':
                    try:
                        price_query = float(search_query)
                        invoices = invoices.filter(
                            Q(total_price=price_query)
                        )
                    except ValueError:
                        try:
                            date_query = datetime.strptime(search_query, "%B %d, %Y, %I:%M %p")
                            invoices = invoices.filter(
                                Q(date__date=date_query.date())
                            )
                        except ValueError:
                            try:
                                invoices = invoices.filter(
                                    Q(customer__id=search_query)
                                )
                            except ValueError:
                                try:
                                    invoices = invoices.filter(
                                        Q(id=search_query)
                                    )
                                except ValueError:
                                    invoices = invoices.filter(
                                        Q(id__icontains=search_query)
                                    )
                                except:
                                        invoices = Invoice.objects.annotate(total_price=Sum('items__price')).values('id', 'customer_id', 'total_price', 'date').order_by('-date')


                paginator = Paginator(invoices, per_page=20)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                
                context['invoices'] = page_obj
                context['search_query'] = search_query

        if request.path == '/free_invoice/invoices_detail.html':
                customer_id = request.GET.get('customer_id')
                invoice_id = request.GET.get('invoice_id')
                customer = get_object_or_404(Customer, id=customer_id)
                context['customer'] = customer

                load_template = '/free_invoice/invoices_detail.html'

                print('----////', load_template)

                if invoice_id != None:
                    invoice = get_object_or_404(FreeInvoice, id=invoice_id)
                    items = invoice.freeitems.all()

                    context['invoice'] = invoice
                    context['items'] = items

                    #container_for_invoice = invoice.containers.get()
                    #context['manifest_id'] = container_for_invoice.manifaist


                    context['invoice_in'] = 'invoice_in'
                    context['invoice_id'] = invoice_id
                else:
                     context['invoice_in'] = ''

        if load_template == 'invoices_detail.html':
                customer_id = request.GET.get('customer_id')
                invoice_id = request.GET.get('invoice_id')
                customer = get_object_or_404(Customer, id=customer_id)
                context['customer'] = customer

                if invoice_id != None:
                    invoice = get_object_or_404(Invoice, id=invoice_id)
                    items = invoice.items.all()

                    context['invoice'] = invoice
                    context['items'] = items

                    container_for_invoice = invoice.containers.get()
                    context['manifest_id'] = container_for_invoice.manifaist


                    context['invoice_in'] = 'invoice_in'
                    context['invoice_id'] = invoice_id

                else:
                     context['invoice_in'] = ''

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
            context['customer_id'] = customer.id
            return redirect('home/customer_detail.html', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)

    context['customer_id'] = customer.id
    return redirect(request, 'home/customer_detail.html', context)


@login_required(login_url="/login/")
def customer_detail(request, customer_id):
            
            #context = {}
            customer_id = request.GET.get('customer_id')
            customer = get_object_or_404(Customer, id=customer_id)
            context['customer'] = customer

            context['customer_transaction'] = customer.customer_transactions.all()

            print('222222')

            invoices = customer.invoices.all()

            freeinvoices = customer.freeinvoices.all()
            invoice_summaries = []
            free_invoice_summaries = []

            total_quantity = 0
            free_total_quantity = 0
            total_cbm = 0
            total_price  = 0
            free_total_price = 0
            total_debit = 0 
            free_total_debit = 0
            total_credit = 0
            free_total_credit = 0
            container_id = 0
            container_manifaist = 0
            free_total_rate = 0

            for freeinvoice in freeinvoices:


                # Get all items related to the invoice
                #items = invoice.items.all()
                #print('items =======-======= ', items)

                freeitems = freeinvoice.freeitems.all()

                print('freeitems', freeitems)

                if freeinvoice.status != 'Unpaid':
                    freetransaction = get_object_or_404(Transaction, invoice=freeinvoice)
                else: 
                    freetransaction = 'noTransaction'
                
                free_invoice_summarie = {
                'invoice_id': freeinvoice.id,
                'transaction': freetransaction,
                'transaction_date': freetransaction.date if freeinvoice.status != 'Unpaid' else datetime.min,
                'status': freeinvoice.status,
                'customer_name': freeinvoice.customer.name,
                'total_quantity': freeitems.aggregate(Sum('quantity'))['quantity__sum'],
                'total_rate': freeitems.aggregate(Sum('rate'))['rate__sum'],
                'total_price': freeitems.aggregate(Sum('price'))['price__sum']
            }
                

                if freeinvoice.status == 'Paid':
                    if freetransaction.transaction_type == 'debit': 
                        free_total_debit += freetransaction.amount or 0
                    else:
                        free_total_credit += freetransaction.amount or 0


                free_total_quantity += free_invoice_summarie['total_quantity'] or 0
                free_total_rate += free_invoice_summarie['total_rate'] or 0
                free_total_price += free_invoice_summarie['total_price'] or 0
                free_invoice_summaries.append(free_invoice_summarie)

            for invoice in invoices:

                # Get all items related to the invoice
                items = invoice.items.all()


                if invoice.status != 'Unpaid':
                    transaction = get_object_or_404(Transaction, invoice=invoice)
                else: 
                    transaction = 'noTransaction'

                try:
                    container_for_invoice = invoice.containers.get()
                    print("Container ID:", container_for_invoice.id)

                    container_id = container_for_invoice.id
                    container_manifaist = container_for_invoice.manifaist

                except Container.DoesNotExist:
                    print("No container found for the given invoice.")

                except Container.MultipleObjectsReturned:
                    print("Multiple containers found for the given invoice.")

                # Assuming you have an invoice instance named 'invoice'


                invoice_summary = {
                'invoice_id': invoice.id,
                'transaction': transaction,
                'transaction_date': transaction.date if invoice.status != 'Unpaid' else datetime.min,
                'status': invoice.status,
                'container_id': container_id,
                'container_manifaist': container_manifaist,
                'customer_name': invoice.customer.name,
                'total_quantity': items.aggregate(Sum('quantity'))['quantity__sum'],
                'total_cbm': items.aggregate(Sum('CBM'))['CBM__sum'],
                'total_price': items.aggregate(Sum('price'))['price__sum']
            }
                
                # Calculate and add the quantities, CBM, and price for each item

                if invoice.status == 'Paid':
                    if transaction.transaction_type == 'debit': 
                        total_debit += transaction.amount or 0
                    else:
                        total_credit += transaction.amount or 0
                print('ok')        

                total_quantity += invoice_summary['total_quantity'] or 0
                total_cbm += invoice_summary['total_cbm'] or 0
                total_price += invoice_summary['total_price'] or 0
                invoice_summaries.append(invoice_summary)



            #invoice_summaries = sorted(invoice_summaries, key=lambda x: x['transaction_date'], reverse=True)
            invoice_summaries = sorted(invoice_summaries, key=lambda x: x['container_manifaist'])

            context['invoice_summaries'] = invoice_summaries
            context['free_invoice_summaries'] = free_invoice_summaries

            context['total_debit'] = total_debit
            context['total_credit'] = total_credit
            context['total_quantity'] = total_quantity
            context['total_cbm'] = total_cbm
            context['total_price'] = total_price

            context['free_total_debit'] = free_total_debit
            context['free_total_credit'] = free_total_credit
            context['free_total_quantity'] = free_total_quantity
            context['free_total_cbm'] = free_total_rate
            context['free_total_price'] = free_total_price
        
            print('222222')
            context['customer_id'] = customer.id
            return redirect(request, 'home/customer_detail.html', context)
            #xxreturn redirect('customer_detail', customer_id=customer.id)


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

@login_required(login_url="/login/")
def delete_customer(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        customer.delete()
        messages.success(request, "Customer deleted successfully.")
        return redirect('customers.html')  # Redirect to the desired URL after successful deletion

@login_required(login_url="/login/")
def add_container(request):
    
    succ = 0
    
    if request.method == 'POST':
        form = ContainerForm(request.POST)
        
        if form.is_valid():
            container = form.save(commit=False)
            container.created_date = datetime.now()
            print('---------')

            num_results = Container.objects.filter(id = container.manifaist).count()

            if num_results == 1:
                messages.success(request, "Container with the provided ID already exists.")
            else:
                succ = 1
                container.save()
                messages.success(request, "Container added successfully.")
    else:
        form = ContainerForm()

    containers = Container.objects.all()

    paginator = Paginator(containers, per_page=20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['containers'] = page_obj

    if succ == 0:
        messages.success(request, "Container with the provided ID already exists.")


    print('======',succ)
    context['succ'] = succ
    context['form'] = form
    
    return render(request, 'home/containers.html', context)
    



@login_required(login_url="/login/")
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




@login_required(login_url="/login/")
def invoices(request):
    search_query = request.GET.get('search', '')
    success_message = messages.get_messages(request)
    
    invoices = Invoice.objects.annotate(total_price=Sum('items__price')).values('id', 'customer_id', 'total_price', 'date').order_by('-date')
    
    if search_query != '':
        try:
            price_query = float(search_query)
            # Filter the invoices based on the 'items__price' field
            invoices = invoices.filter(
                items__price=price_query
            )
        except ValueError:
            try:
                date_query = datetime.strptime(search_query, "%B %d, %Y, %I:%M %p")
                invoices = invoices.filter(
                    Q(date__date=date_query.date())
                )
            except ValueError:
                try:
                    # Search by invoice ID directly on the 'id' field
                    invoices = invoices.filter(
                        Q(id__icontains=search_query)
                    )
                except ValueError:
                    invoices = Invoice.objects.annotate(total_price=Sum('items__price')).order_by('-date')

    paginator = Paginator(invoices, per_page=20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    success_messages = messages.get_messages(request)
    for message in success_messages:
        success_message = str(message)
        break
    
    success_message = None

    context = {
        'invoices': page_obj,
        'search_query': search_query,
        'success_message': success_message,
    }
    return render(request, 'home/invoices.html', context)


@login_required(login_url="/login/")   
def generate_invoice_id():
    timestamp = timezone.now().strftime("%y%m%d%H%M%S")
    random_string = get_random_string(
        length=7, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    return f"MRSU{timestamp}{random_string}"

@login_required(login_url="/login/")
def Invoice_save(request):
    if request.method == "POST":
        invoice_items = json.loads(request.body)
        totalprice = 0
        totalcbm = 0
        totalpack = 0
        customer = None
        items = []

        print("<><><><><======><><><><>")
        customer = Customer.objects.get(id=invoice_items[0]["id_customer"])

        if invoice_items[0]["invoice_in"] == 'invoice_in':

            #print("invoice id ======><><><><>", invoice_items[0])

            invoice = Invoice.objects.get(id = invoice_items[0]["invoice_id"])
            items_for_invoice = invoice.items.all()
            items_for_invoice.delete()  
        
        else:

            invoice = Invoice(customer=customer)
            invoice.save()  # Save the invoice to obtain the ID
        
        for item in invoice_items:
            
            item_obj = Item(
                invoice=invoice,
                item=item["item"],
                source=item["source"],
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

        if invoice_items[0]["invoice_in"] != 'invoice_in':
            container, create = Container.objects.get_or_create(manifaist=item["manifest"])

            #print('----------->',container)
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

        if invoice_items[0]["invoice_in"] == 'invoice_in':
            messages.success(request, "invoice edited successfully.")
            invoice_items[0]["invoice_in"] = 'invoice_out'
        else:
            messages.success(request, "invoice saved successfully.")

        load_template = 'final_invoice.html'
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    else:
        return JsonResponse({"error": "Invalid request method"})
    



@login_required(login_url="/login/")
def free_invoice_save(request):

    if request.method == "POST":
        invoice_items = json.loads(request.body)
        totalprice = 0
        totalpack = 0
        customer = None
        items = []

        print("<><><><><==--==><><><><>")
        customer = Customer.objects.get(id=invoice_items[0]["id_customer"])

        if invoice_items[0]["invoice_in"] == 'invoice_in':

            #print("invoice id ======><><><><>", invoice_items[0])

            invoice = FreeInvoice.objects.get(id = invoice_items[0]["invoice_id"])
            items_for_invoice = invoice.freeitems.all()
            items_for_invoice.delete()  
        
        else:

            invoice = FreeInvoice(customer=customer)
            invoice.save()  # Save the invoice to obtain the ID
        
        for item in invoice_items:
            
            item_obj = FreeItem(
                invoice=invoice,
                item=item["item"],
                quantity=item["quantity"],
                rate=item["rate"],
                price=item["price"]
            )
            item_obj.save()

            items.append(item_obj)

            totalprice += item["price"]
            totalpack += item["quantity"]

        context['totalprice'] = totalprice
        context['totalpack'] = totalpack

        context['customer'] = customer
        context['invoice'] = invoice
        context['items'] = items

        if invoice_items[0]["invoice_in"] == 'invoice_in':
            messages.success(request, "free invoice edited successfully.")
            invoice_items[0]["invoice_in"] = 'invoice_out'
        else:
            messages.success(request, "free invoice saved successfully.")

        load_template = '/free_invoice/invoice_view.html'
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    else:
        return JsonResponse({"error": "Invalid request method"})

def save_images(request):
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')
        images = request.FILES.values()
        saved_images = []

        for image in images:
            # Read the image file and get the byte data
            image_data = image.read()

            # Create and store the InvoiceImage instance in the list
            invoice_image = InvoiceImage(invoice_id=invoice_id, image_data=image_data)
            saved_images.append(invoice_image)

        # Save all the InvoiceImage instances
        InvoiceImage.objects.bulk_create(saved_images)

        return JsonResponse({'message': 'Images saved successfully'})
    return JsonResponse({'message': 'Invalid request method'}, status=400)

def get_invoice_images(request):
    if request.method == 'GET':
        invoice_id = request.GET.get('invoice_id')

        try:
            images = InvoiceImage.objects.filter(invoice_id=invoice_id)
            image_data = [image.image_data for image in images]
            image_urls = [f'data:image/jpeg;base64,{base64.b64encode(image).decode("utf-8")}' for image in image_data]
            return JsonResponse(image_urls, safe=False)
        except InvoiceImage.DoesNotExist:
            return JsonResponse([], safe=False)

    return JsonResponse({'message': 'Invalid request method'}, status=400)


def delete_invoice(request):
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            # Store the customer ID before deleting the invoice
            customer_id = invoice.customer.id
            invoice.delete()
            messages.success(request, 'Invoice deleted successfully')

            # Check the session variable to determine the source of the request
            from_page = request.session.get('delete_invoice_from_page')
            if from_page == 'customer_detail':
                # Redirect to the customer_detail page with the appropriate customer_id
                context['customer_id'] = customer_id
                return redirect('home/customer_detail.html', context)
            else:
                return redirect('invoices')  # Replace 'invoices' with the appropriate URL name of the invoices page

        except Invoice.DoesNotExist:
            messages.error(request, 'Invoice not found')
    else:
        messages.error(request, 'Invalid request')

    return redirect('invoices')  # Replace 'invoices' with the appropriate URL name of the invoices page

def delete_free_invoice(request):
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')
        try:
            invoice = FreeInvoice.objects.get(id=invoice_id)
            customer = invoice.customer
            invoice.delete()
            messages.success(request, 'Invoice deleted successfully')

        except FreeInvoice.DoesNotExist:
            messages.error(request, 'Invoice not found')
    else:
        messages.error(request, 'Invalid request')

    #request.GET['customer_id'] = customer.id
    context['customer_id'] = customer.id
    #print('customer.id', customer.id)
    return redirect('home/customer_detail.html', context)  # Replace 'invoices' with the appropriate URL name of the invoices page


def cencel_freetransanction(request):
    if request.method == 'POST':

        invoice_id = request.POST.get('invoice_id')
        customer_id = request.POST.get('customer_id')

        try:
            invoice = FreeInvoice.objects.get(id=invoice_id)
            transaction = FreeTransaction.objects.get(invoice=invoice)

            customer = Customer.objects.get(id=customer_id)

            invoice.status = 'Unpaid'
            invoice.save()

            if transaction.transaction_type == 'debit':  
                customer.balance =  customer.balance - transaction.amount
            else:

                print('total: ', transaction.rest)
                print('amount paid: ',transaction.amount)
                x = transaction.rest - transaction.amount
                print('balance ols: ',customer.balance )
                customer.balance =  customer.balance + x
                print('diff paid: ', x)
                print('balance now: ',customer.balance )
            customer.save()
            transaction.delete()

            messages.success(request, 'Transaction Cencel successfully')

        except Invoice.DoesNotExist:
            messages.error(request, 'Transaction not found')
    else:
        messages.error(request, 'Transaction request')

    context['customer_id'] = customer_id
    #print('customer.id', customer.id)
    return redirect('home/customer_detail.html', context)  





def cencel_transanction(request):
    if request.method == 'POST':

        invoice_id = request.POST.get('invoice_id')
        customer_id = request.POST.get('customer_id')

        try:
            invoice = Invoice.objects.get(id=invoice_id)
            transaction = Transaction.objects.get(invoice=invoice)

            customer = Customer.objects.get(id=customer_id)

            invoice.status = 'Unpaid'
            invoice.save()

            if transaction.transaction_type == 'debit':  
              customer.balance =  customer.balance - transaction.amount
            else:
                print('total: ', transaction.rest)
                print('amount paid: ',transaction.amount)
                x = transaction.rest - transaction.amount
                print('balance ols: ',customer.balance )
                customer.balance =  customer.balance + x
                print('diff paid: ', x)
                print('balance now: ',customer.balance )
              
            customer.save()

            invoice.save()
            transaction.delete()

            messages.success(request, 'Transaction Cencel successfully')

        except Invoice.DoesNotExist:
            messages.error(request, 'Transaction not found')
    else:
        messages.error(request, 'Transaction request')
        
    context['customer_id'] = customer_id
    return redirect('home/customer_detail.html', customer_id=customer_id)  # Replace 'invoices' with the appropriate URL name of the invoices page



def change_balance(request):

    if request.method == 'POST':

        amount = float(request.POST.get('amount'))
        option = request.POST.get('option')

        


        customer_id = request.POST.get('customer_id')
        customer = Customer.objects.get(id=customer_id)

        try:

            customer = Customer.objects.get(id=customer_id)
            
            CustomerTransaction.objects.create(
                customer=customer,
                amount=amount,
                init=customer.balance,
                transaction_type=option,
                date=timezone.now()
            )

            if option == 'credit':
                customer.balance = float(customer.balance) + amount
            else: 
                 customer.balance = float(customer.balance) - amount

            

            customer.save()

            messages.success(request, 'Nice Transaction')

        except Invoice.DoesNotExist:
            messages.error(request, 'Transaction not found')
    else:
        messages.error(request, 'Transaction request')
    context['customer_id'] = customer_id

    return redirect('home/customer_detail.html', customer_id=customer_id)  # Replace 'invoices' with the appropriate URL name of the invoices page




def change_free_invoice_status(request):

    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')
        customer_id = request.POST.get('customer_id')
        totalprice = float(request.POST.get('totalprice'))

        option = request.POST.get('option')
        amount = float(str(request.POST.get('amount')))

        customer = Customer.objects.get(id=customer_id)
        balance = float(customer.balance)
        
        if option == 'credit':
            dif = amount - totalprice 
            balance = balance + dif
        else:
            balance =  amount - balance

        customer.balance = balance

        print("amount :", amount)
        print("totalprice :", totalprice)
        print("balance :", balance)
 

        try:
            invoice = FreeInvoice.objects.get(id=invoice_id)

            FreeTransaction.objects.create(
                invoice=invoice,
                amount=amount,
                rest=totalprice,
                transaction_type=option,
                date=timezone.now(),
            )

            invoice.status = 'Paid'
            invoice.save()
            customer.save()
            messages.success(request, 'Invoice status change successfully')

        except Invoice.DoesNotExist:
            messages.error(request, 'Invoice not found')
    else:
        messages.error(request, 'Invalid request')
        invoice = get_object_or_404(FreeInvoice, id=invoice_id)

    #context['customer_id'] = customer_id
    
    #load_template = 'customer_detail.html'

    context['customer_id'] = customer.id
    #print('customer.id', customer.id)
    return redirect('home/customer_detail.html', context)  

    #invoice_view.html?invoice_id={{ invoice_summary.invoice_id }}

    #return redirect('invoices')  # Replace 'invoices' with the appropriate URL name of the invoices page

def change_invoice_status(request):

    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')
        customer_id = request.POST.get('customer_id')
        totalprice = float(request.POST.get('totalprice'))

        option = request.POST.get('option')
        amount = float(request.POST.get('amount'))

        customer = Customer.objects.get(id=customer_id)
        balance = float(customer.balance)
        
        if option == 'credit':
            dif = amount - totalprice 
            balance = balance + dif
        else:
            balance = amount - balance
        
        customer.balance = balance

        print("amount :", amount)
        print("totalprice :", totalprice)
        print("dif :", dif)
        print("balance :", balance)
 

        try:
            invoice = Invoice.objects.get(id=invoice_id)

            Transaction.objects.create(
                invoice=invoice,
                amount=amount,
                rest=totalprice,
                transaction_type=option,
                date=timezone.now(),
            )

            invoice.status = 'Paid'
            invoice.save()
            customer.save()
            messages.success(request, 'Invoice status change successfully')

        except Invoice.DoesNotExist:
            messages.error(request, 'Invoice not found')
    else:
        messages.error(request, 'Invalid request')
        invoice = get_object_or_404(Invoice, id=invoice_id)

    #context['customer_id'] = customer_id
    
    #load_template = 'customer_detail.html'
    context['customer_id'] = customer.id

    return redirect('home/customer_detail.html', customer_id=customer_id)

    #invoice_view.html?invoice_id={{ invoice_summary.invoice_id }}

    #return redirect('invoices')  # Replace 'invoices' with the appropriate URL name of the invoices page



def generate_pdf(request):
    

    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')
        print(invoice_id)
        invoice = get_object_or_404(Invoice, id=invoice_id)

        invoice_summaries = []
        context = {}

        container = invoice.containers.first() 

        if container:
            container_data = {
                'id': container.id,
                'status': container.status,
                'size': container.size,
                'manifaist': container.manifaist,
                'created_date': container.created_date,
                'invoice_id': invoice.id,
            }

        #print("containers", container_data)
        # Get all items related to the invoice
        items = invoice.items.all()
            
        context['invoice_summaries'] = invoice_summaries
        context['container_data'] = container_data
        context['invoice'] = invoice
        context['customer'] = invoice.customer
        context['totalpack'] = items.aggregate(s=Sum("quantity"))["s"]
        context['totalcbm'] = items.aggregate(s=Sum("CBM"))["s"]
        context['totalprice'] = items.aggregate(s=Sum("price"))["s"]
        # Your dynamic data (replace this with your data logic)

        # Path to the directory containing the HTML template and the image

        image_file_logo = "apps/static/assets/img/theme/tet.png"
        image_file_bankili = "apps/static/assets/img/theme/bankili.png"

        image_logo = image_file_logo

        image_bankili = image_file_bankili

        # Render the template with dynamic data and image data
        template = 'home/invoice_style_pdf.html'

        #html_template = loader.get_template('invoice_style_pdf.html')

        context['image_logo'] = image_logo
        context['image_bankili'] = image_bankili
        context['items'] = items

        if len(items) >= 9:

            template = loader.get_template('home/invoice_no_foot.html') 
            context['items'] = items[:10] 
            html = template.render(context) 
            result1 = BytesIO()
            pdf1 = pisa.pisaDocument(StringIO(html), dest=result1)

            template = get_template('home/second_invoice_style_pdf.html') 
            context['items'] = items[10:] 
            html = template.render(context) 
            result2 = BytesIO()
            pdf1 = pisa.pisaDocument(StringIO(html), dest=result2)

            # Reset the file pointers of the generated PDFs
            result1.seek(0)
            result2.seek(0)

            # Create a PDF merger object
            pdf_merger = PyPDF2.PdfMerger()
            pdf_merger.append(result1)
            pdf_merger.append(result2)
            merged_pdf_buffer = BytesIO()
            pdf_merger.write(merged_pdf_buffer)
            merged_pdf_buffer.seek(0)
            print("too")

            response =  HttpResponse(merged_pdf_buffer.getvalue(), content_type='application/pdf') 
            response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
            return response
        else:
            template = get_template(template) 
            html = template.render(context) 
            result = BytesIO()
            pisa.pisaDocument(StringIO(html), dest=result) 
                

            response =  HttpResponse(result.getvalue(), content_type='application/pdf', ) 
            response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
            return response
        
    return HttpResponse('Errors')


def generate_free_pdf(request):


        invoice_id = request.POST.get('invoice_id')
        invoice = get_object_or_404(FreeInvoice, id=invoice_id)

        invoice_summaries = []

        #print("containers", container_data)
        # Get all items related to the invoice
        items = invoice.freeitems.all()
            
        context['invoice_summaries'] = invoice_summaries
        context['invoice'] = invoice
        context['customer'] = invoice.customer
        context['totalpack'] = items.aggregate(s=Sum("quantity"))["s"]
        context['totalprice'] = items.aggregate(s=Sum("price"))["s"]

        # Load the new 'transaction.style.pdf.html' template
        template = get_template('home/free_invoice/free_invoice_pdf.html')
        html = template.render(context)

        # Generate the PDF
        pdf_file = BytesIO()
        pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=pdf_file)

        # Set the response headers to trigger the download
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="transaction_{invoice.id}.pdf"'
        response.write(pdf_file.getvalue())

        return response
'''
def cancel_transanction_balance(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        # Retrieve the specific transaction based on the transaction_id
        transaction = get_object_or_404(CustomerTransaction, id=transaction_id)

        # Perform the deletion of the transaction
        transaction.delete()

        # Add a success message
        messages.success(request, 'Transaction deleted successfully.')

    return redirect('customer_detail', customer_id=transaction.customer_id)
'''


def generate_transaction_pdf(request):

    if request.method == 'POST':
        
        transaction_id = request.POST.get('transaction_id')
        # Retrieve the specific transaction based on the transaction_id
        transaction = get_object_or_404(CustomerTransaction, id=transaction_id)

        context = {
            'transaction': transaction,
            # Add any other relevant data to the context
        }

        # Load the new 'transaction.style.pdf.html' template
        template = get_template('home/transaction.style.pdf.html')
        html = template.render(context)

        # Generate the PDF
        pdf_file = BytesIO()
        pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=pdf_file)

        # Set the response headers to trigger the download
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="transaction_{transaction.id}.pdf"'
        response.write(pdf_file.getvalue())

    return response

from decimal import Decimal

def cancel_transanction_balance(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        # Retrieve the specific transaction based on the transaction_id
        transaction = get_object_or_404(CustomerTransaction, id=transaction_id)

        # Check the transaction type
        if transaction.transaction_type == 'debit':
            # If it's a debit transaction, add the amount to the customer's balance
            customer = Customer.objects.get(id=transaction.customer_id)
            customer.balance += Decimal(str(transaction.amount))
            customer.save()
        elif transaction.transaction_type == 'credit':
            # If it's a credit transaction, subtract the amount from the customer's balance
            customer = Customer.objects.get(id=transaction.customer_id)
            customer.balance -= Decimal(str(transaction.amount))
            customer.save()

        # Perform the deletion of the transaction
        transaction.delete()

        # Add a success message
        messages.success(request, 'Transaction deleted successfully.')
    context['customer_id'] = customer.id

    return redirect('home/customer_detail.html', customer_id=transaction.customer_id)