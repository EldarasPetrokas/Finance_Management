from django.shortcuts import render, get_object_or_404, redirect
from .models import Invoice, Client
from .forms import ClientForm, InvoiceForm, ContactPersonForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
import os
import json
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta


def index(request):
    # Get invoice statistics
    total_invoices = Invoice.objects.count()
    paid_invoices = Invoice.objects.filter(status='paid').count()
    issued_invoices = Invoice.objects.filter(status='issued').count()
    overdue_invoices = Invoice.objects.filter(status='overdue').count()
    
    # Get recent invoices
    recent_invoices = Invoice.objects.all().order_by('-entry_date')[:5]
    
    # Get monthly data for chart
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_data = Invoice.objects.filter(entry_date__gte=six_months_ago) \
        .annotate(month=TruncMonth('entry_date')) \
        .values('month') \
        .annotate(total=Sum('sum')) \
        .order_by('month')
    
    monthly_labels = [item['month'].strftime('%b %Y') for item in monthly_data]
    monthly_amounts = [float(item['total']) for item in monthly_data]
    
    context = {
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'issued_invoices': issued_invoices,
        'overdue_invoices': overdue_invoices,
        'recent_invoices': recent_invoices,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': monthly_amounts,
    }
    
    return render(request, 'index.html', context)


def invoice_list(request):
    sort_by = request.GET.get('sort', 'client')  # Default sort by client name
    status_filter = request.GET.get('status', '')
    
    # Define sorting logic
    if sort_by == 'client':
        invoices = Invoice.objects.all().order_by('client__name')  # Sort by client name
    elif sort_by == 'amount':
        invoices = Invoice.objects.all().order_by('sum')  # Sort by amount
    elif sort_by == 'status':
        invoices = Invoice.objects.all().order_by('status')  # Sort by status
    else:
        invoices = Invoice.objects.all()  # Default, no sorting
    
    # Apply status filter if provided
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    # Return JSON response if requested
    if request.GET.get('format') == 'json':
        invoice_data = []
        for invoice in invoices:
            invoice_data.append({
                'id': str(invoice.id),
                'client_name': invoice.client.name,
                'sum': str(invoice.sum),
                'status': invoice.status,
                'status_display': invoice.get_status_display(),
                'payment_date': invoice.payment_date.strftime('%Y-%m-%d') if invoice.payment_date else '',
            })
        return JsonResponse({'invoices': invoice_data})
    
    return render(request, 'invoices_list.html', {'invoices': invoices})


def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    return render(request, 'invoice_detail.html', {'invoice': invoice})


def client_list(request):
    clients = Client.objects.all()  # Get all clients
    return render(request, 'clients_list.html', {'clients': clients})


def mark_as_paid(request):
    if request.method == "POST":
        invoice_ids = request.POST.getlist('invoice_ids')  # Get selected invoice IDs
        invoices = Invoice.objects.filter(id__in=invoice_ids)  # Filter invoices
        invoices.update(status='paid')  # Update the status to "payed"
    return redirect('invoice_list')  # Redirect back to the invoice list


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def send_reminder(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if invoice.status == 'overdue' and not invoice.reminder_sent:
        try:
            if invoice.send_reminder_email():
                messages.success(request, f"Reminder sent to Contact Person for Invoice #{invoice.id}!")
            else:
                messages.warning(request, "Reminder could not be sent due to invalid conditions.")
        except Exception as e:
            messages.error(request, f"Failed to send reminder: {str(e)}")
    else:
        messages.warning(request, "Reminder not sent as it has already been sent or is not overdue.")
    return redirect('invoice_detail', invoice_id=invoice.id)


@login_required
def add_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Client added successfully!")
            return redirect('client_list')  # Redirect to a client list view
    else:
        form = ClientForm()
    return render(request, 'add_client.html', {'form': form})


@login_required
def add_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()  # This should trigger the `save()` method in the model
            return redirect('invoice_list')  # Redirect to the invoices list after saving
    else:
        form = InvoiceForm()
    return render(request, 'add_invoice.html', {'form': form})


@login_required
def add_contact_person(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = ContactPersonForm(request.POST)
        if form.is_valid():
            contact_person = form.save(commit=False)
            contact_person.client = client  # Associate the contact person with the client
            contact_person.save()
            messages.success(request, f"Contact person added for client {client.name}!")
            return redirect('client_detail', client_id=client.id)  # Redirect to the client detail view
    else:
        form = ContactPersonForm()

    return render(request, 'add_contact_person.html', {'form': form, 'client': client})


@login_required
def client_detail(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    return render(request, 'client_detail.html', {'client': client})


def download_invoice(request, invoice_id):
    try:
        # Fetch the invoice
        invoice = Invoice.objects.get(id=invoice_id)
        pdf_path = invoice.pdf_file_path

        # Check if the file exists
        if not os.path.exists(pdf_path):
            raise Http404("PDF not found.")

        # Serve the file
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    except Invoice.DoesNotExist:
        raise Http404("Invoice not found.")
