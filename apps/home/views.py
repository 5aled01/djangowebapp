# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""


# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import PyPDF2
import io
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
from .models import Customer, Container, InvoiceImage, Item, Invoice



from xhtml2pdf import pisa
from io import StringIO, BytesIO
from django.template.loader import get_template 
from django.template import Context


context = {}

@login_required(login_url="/login/")
def index(request):
    customer_count = Customer.objects.count()
    total_income = Item.objects.aggregate(total=Sum('price'))['total'] or 0
    total_expenses = Container.objects.aggregate(total=Sum('price'))['total'] or 0

    three_days_ago = timezone.now() - timedelta(days=3)

    new_customer_count = Customer.objects.filter(created_date__gte=three_days_ago).count()

    sum_of_prices = Item.objects.filter(created_date__gte=three_days_ago).aggregate(total_price=Sum('price'))['total_price'] or 0
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

            paginator = Paginator(customers, per_page=4)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['customers'] = page_obj

        if load_template == 'customer_detail.html':
            customer_id = request.GET.get('customer_id')
            customer = get_object_or_404(Customer, id=customer_id)
            context['customer'] = customer
        
        if load_template == 'invoice_view.html':
            invoice_id = request.GET.get('invoice_id')
            invoice = get_object_or_404(Invoice, id=invoice_id)

            invoice_summaries = []

            total_quantity = 0
            total_cbm = 0
            total_price = 0
            print('----', invoice.id)
                # Get all items related to the invoice
            items = invoice.items.all()
         
            context['invoice_summaries'] = invoice_summaries
            context['invoice'] = invoice
            context['customer'] = invoice.customer
            context['items'] = items 
            context['totalpack'] = items.aggregate(s=Sum("quantity"))["s"]
            context['totalcbm'] = items.aggregate(s=Sum("CBM"))["s"]
            context['totalprice'] = items.aggregate(s=Sum("price"))["s"]

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
                    'id', 'created_date', 'size', 'status')).filter(search=search_query)

            else:
                containers = Container.objects.all()

            paginator = Paginator(containers, per_page=4)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['containers'] = page_obj

        if load_template == 'invoices.html':
                search_query = request.GET.get('search', '')

                invoices = Invoice.objects.annotate(total_price=Sum('items__price')).values('id', 'customer_id', 'total_price', 'date')

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
                                uuid.UUID(search_query)  # Check if search_query is a valid UUID
                                invoices = invoices.filter(
                                    Q(customer__id=search_query)
                                )
                            except ValueError:
                                invoices = invoices.filter(
                                    Q(id__icontains=search_query)
                                )
                            except:
                                invoices = Invoice.objects.annotate(total_price=Sum('items__price')).values('id', 'customer_id', 'total_price', 'date')


                paginator = Paginator(invoices, per_page=4)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                
                context['invoices'] = page_obj
                context['search_query'] = search_query


        if load_template == 'invoices_detail.html':
                customer_id = request.GET.get('customer_id')
                customer = get_object_or_404(Customer, id=customer_id)
                context['customer'] = customer
        
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

            num_results = Container.objects.filter(id = container.id).count()

            if num_results == 1:
                messages.success(request, "Container with the provided ID already exists.")
            else:
                succ = 1
                container.save()
                messages.success(request, "Container added successfully.")
    else:
        form = ContainerForm()

    containers = Container.objects.all()

    paginator = Paginator(containers, per_page=4)
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
    invoices = Invoice.objects.annotate(total_price=Sum('items__price')).values('id', 'customer_id', 'total_price', 'date')

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
                    uuid.UUID(search_query)  # Check if search_query is a valid UUID
                    invoices = invoices.filter(
                        Q(customer__id=search_query)
                    )
                except ValueError:
                    invoices = invoices.filter(
                        Q(id__icontains=search_query)
                    )
                except:
                    pass      

    paginator = Paginator(invoices, per_page=4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    success_messages = messages.get_messages(request)
    success_message = None
    for message in success_messages:
        success_message = str(message)
        break

    context['invoices'] = page_obj
    context['search_query'] = search_query
    context['success_message']= success_message
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

        customer = Customer.objects.get(id=invoice_items[0]["id_customer"])
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

        messages.success(request, "invoice saved successfully.")

        load_template = 'final_invoice.html'
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
            invoice.delete()
            messages.success(request, 'Invoice deleted successfully')
        except Invoice.DoesNotExist:
            messages.error(request, 'Invoice not found')
    else:
        messages.error(request, 'Invalid request')

    return redirect('invoices')  # Replace 'invoices' with the appropriate URL name of the invoices page




def generate_pdf(request):
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')
        print(invoice_id)
        invoice = get_object_or_404(Invoice, id=invoice_id)

        invoice_summaries = []
        context = {}

        # Get all items related to the invoice
        items = invoice.items.all()
            
        context['invoice_summaries'] = invoice_summaries
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
        context['image_logo'] = image_logo
        context['image_bankili'] = image_bankili
        context['items'] = items

        if len(items) >= 9:
            # Merge multiple PDFs into a single compressed PDF
            merged_pdf_buffer = compress_multiple_pdfs(template, context, items)
            response = HttpResponse(merged_pdf_buffer.getvalue(), content_type='application/pdf')
        else:
            # Generate a single PDF and compress it
            pdf_buffer = generate_single_pdf(template, context)
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')

        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
        return response
        
    return HttpResponse('Errors')

def generate_single_pdf(template, context):
    html_template = loader.get_template(template)
    html = html_template.render(context)
    result = io.BytesIO()
    pisa.pisaDocument(io.StringIO(html), dest=result)
    return compress_pdf(result)

def compress_pdf(pdf_buffer):
    # Create a PDF reader object from the buffer
    pdf_reader = PyPDF2.PdfReader(pdf_buffer)

    # Create a PDF writer object
    pdf_writer = PyPDF2.PdfWriter()

    # Add pages from the input PDF to the writer object
    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    # Write the compressed PDF to a new buffer
    compressed_pdf_buffer = io.BytesIO()
    pdf_writer.write(compressed_pdf_buffer)
    compressed_pdf_buffer.seek(0)

    return compressed_pdf_buffer

def compress_multiple_pdfs(template, context, items):
    # Split items into chunks of 10 (to avoid excessive PDF page count)
    chunked_items = [items[i:i+10] for i in range(0, len(items), 10)]

    # Create an empty list to store the compressed PDF buffers
    compressed_pdfs = []

    # Generate and compress each chunk separately
    for chunk in chunked_items:
        pdf_buffer = generate_single_pdf(template, context)
        compressed_pdf_buffer = compress_pdf(pdf_buffer)
        compressed_pdfs.append(compressed_pdf_buffer)

    # Create a PDF merger object
    pdf_merger = PyPDF2.PdfMerger()

    # Append each compressed PDF to the merger
    for compressed_pdf_buffer in compressed_pdfs:
        pdf_merger.append(compressed_pdf_buffer)

    # Merge the PDFs into a single compressed PDF
    merged_pdf_buffer = io.BytesIO()
    pdf_merger.write(merged_pdf_buffer)
    merged_pdf_buffer.seek(0)

    return merged_pdf_buffer
