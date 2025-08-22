from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, HttpResponseForbidden
from .models import Receipt
from .forms import ReceiptForm
from apps.invoices.models import Invoice
from django.db.models import Sum, Count
from django.utils import timezone
import openpyxl
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.http import HttpResponse
import os
import urllib.parse
from apps.core.models import CompanyProfile
from apps.core.utils import get_company_context
import base64

# Staff check
def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

def get_filtered_receipts(request):
    # Filter receipts by the current user who created them
    receipts = Receipt.objects.filter(created_by=request.user).select_related('invoice')
    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    status = request.GET.get('status', '')
    amount = request.GET.get('amount', '')
    payment_method = request.GET.get('payment_method', '')
    received_by = request.GET.get('received_by', '')
    if search:
        receipts = receipts.filter(client_name__icontains=search)
    if date_from:
        receipts = receipts.filter(date_received__gte=date_from)
    if date_to:
        receipts = receipts.filter(date_received__lte=date_to)
    if status:
        receipts = receipts.filter(invoice__status=status)
    if amount:
        try:
            amount_val = float(amount.replace(',', ''))
            receipts = receipts.filter(amount_received=amount_val)
        except ValueError:
            pass
    if payment_method:
        receipts = receipts.filter(payment_method=payment_method)
    if received_by:
        receipts = receipts.filter(received_by__icontains=received_by)
    return receipts

@login_required
def receipt_list_view(request):
    """List all receipts with search/filter and dashboard stats."""
    receipts = get_filtered_receipts(request)
    # Dashboard stats
    today = timezone.now().date()
    week_start = today - timezone.timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    stats = {
        'total_today': receipts.filter(date_received=today).aggregate(Sum('amount_received'))['amount_received__sum'] or 0,
        'total_week': receipts.filter(date_received__gte=week_start).aggregate(Sum('amount_received'))['amount_received__sum'] or 0,
        'total_month': receipts.filter(date_received__gte=month_start).aggregate(Sum('amount_received'))['amount_received__sum'] or 0,
        'top_clients': receipts.values('client_name').annotate(total=Sum('amount_received')).order_by('-total')[:5],
        'by_method': receipts.values('payment_method').annotate(total=Sum('amount_received')).order_by('-total'),
    }
    
    # Get company context for currency
    company_context = get_company_context(request.user)
    
    context = {
        'receipts': receipts.order_by('-date_received', '-created_at'),
        'search': request.GET.get('search', ''),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'stats': stats,
        'company_profile': company_context['company_profile'],
        'user_currency_symbol': company_context['currency_symbol'],
        'user_currency_code': company_context['currency_code'],
    }
    return render(request, 'receipts/receipt_list.html', context)

@login_required
@staff_required
def receipt_create_view(request, invoice_id=None):
    """Create a new receipt, optionally linked to an invoice."""
    invoice = None
    if invoice_id:
        invoice = get_object_or_404(Invoice, pk=invoice_id)
    if request.method == 'POST':
        form = ReceiptForm(request.POST, invoice=invoice, user=request.user)
        if form.is_valid():
            receipt = form.save(commit=False)
            # Set the actual user who created the receipt for audit
            if not receipt.pk:
                receipt.created_by = request.user
            # Do NOT set receipt.received_by = request.user; use the typed value from the form
            # Calculate balance after payment
            if invoice:
                total_received = sum(r.amount_received for r in invoice.receipts.all()) + form.cleaned_data['amount_received']
                receipt.balance_after_payment = invoice.grand_total - total_received
            else:
                receipt.balance_after_payment = 0
            receipt.save()
            messages.success(request, f'Receipt {receipt.receipt_no} created successfully!')
            return redirect('receipts:detail', receipt_id=receipt.pk)
    else:
        form = ReceiptForm(invoice=invoice, user=request.user)
    
    # Get company context for currency
    company_context = get_company_context(request.user)
    
    context = {
        'form': form, 
        'invoice': invoice,
        'user_currency_symbol': company_context['currency_symbol'],
        'user_currency_code': company_context['currency_code'],
    }
    return render(request, 'receipts/receipt_form.html', context)

@login_required
def receipt_detail_view(request, receipt_id):
    """Show receipt details, print/export options, and audit log."""
    receipt = get_object_or_404(Receipt, pk=receipt_id, created_by=request.user)
    
    # Get company context for currency from current user
    company_context = get_company_context(request.user)
    company_profile = company_context['company_profile']
    company_logo = company_context['company_logo']
    company_signature = company_context['company_signature']
    
    context = {
        'receipt': receipt, 
        'company_profile': company_profile, 
        'company_logo': company_logo, 
        'company_signature': company_signature,
        'user_currency_symbol': company_context['currency_symbol'],
        'user_currency_code': company_context['currency_code'],
    }
    return render(request, 'receipts/receipt_detail.html', context)

@login_required
@staff_required
def receipt_edit_view(request, receipt_id):
    """Edit an existing receipt."""
    receipt = get_object_or_404(Receipt, pk=receipt_id, created_by=request.user)
    if request.method == 'POST':
        form = ReceiptForm(request.POST, instance=receipt, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Receipt {receipt.receipt_no} updated successfully!')
            return redirect('receipts:detail', receipt_id=receipt.pk)
    else:
        form = ReceiptForm(instance=receipt, user=request.user)
    
    # Get company context for currency
    company_context = get_company_context(request.user)
    
    context = {
        'form': form, 
        'receipt': receipt,
        'user_currency_symbol': company_context['currency_symbol'],
        'user_currency_code': company_context['currency_code'],
    }
    return render(request, 'receipts/receipt_form.html', context)

@login_required
@staff_required
def receipt_delete_view(request, receipt_id):
    """Delete a receipt (staff only)."""
    receipt = get_object_or_404(Receipt, pk=receipt_id, created_by=request.user)
    if request.method == 'POST':
        receipt.delete()
        messages.success(request, f'Receipt {receipt.receipt_no} deleted.')
        return redirect('receipts:list')
    context = {'receipt': receipt}
    return render(request, 'receipts/receipt_confirm_delete.html', context)

@login_required
def receipt_print_view(request, receipt_id):
    """Print-friendly view of the receipt."""
    receipt = get_object_or_404(Receipt, pk=receipt_id, created_by=request.user)
    
    # Get company context for currency from current user
    company_context = get_company_context(request.user)
    company_profile = company_context['company_profile']
    company_logo = company_context['company_logo']
    company_signature = company_context['company_signature']
    
    context = {
        'receipt': receipt, 
        'company_profile': company_profile, 
        'company_logo': company_logo, 
        'company_signature': company_signature,
        'user_currency_symbol': company_context['currency_symbol'],
        'user_currency_code': company_context['currency_code'],
    }
    return render(request, 'receipts/receipt_print.html', context)

@login_required
def receipt_pdf_view(request, receipt_id):
    """Export receipt as PDF with status display."""
    receipt = get_object_or_404(Receipt, pk=receipt_id, created_by=request.user)
    
    # Get company context for currency from current user
    company_context = get_company_context(request.user)
    company_profile = company_context['company_profile']
    company_logo = company_context['company_logo']
    company_signature = company_context['company_signature']
    
    context = {
        'receipt': receipt, 
        'company_profile': company_profile, 
        'company_logo': company_logo, 
        'company_signature': company_signature,
        'user_currency_symbol': company_context['currency_symbol'],
        'user_currency_code': company_context['currency_code'],
    }
    
    try:
        from xhtml2pdf import pisa
        from django.template.loader import render_to_string
        from io import BytesIO
        html_string = render_to_string('receipts/receipt_pdf_template.html', context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.receipt_no}.pdf"'
            return response
        else:
            return HttpResponse("Error generating PDF", content_type="text/plain", status=500)
    except ImportError:
        return HttpResponse("xhtml2pdf is not installed. Please install it: pip install xhtml2pdf", content_type="text/plain", status=500)

@login_required
def receipt_email_view(request, receipt_id):
    """Send receipt to client via email (stub)."""
    receipt = get_object_or_404(Receipt, pk=receipt_id, created_by=request.user)
    # TODO: Implement email sending
    messages.info(request, 'Email feature not implemented yet.')
    return redirect('receipts:detail', receipt_id=receipt.pk)

@login_required
def export_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Receipts"
    headers = ["Receipt #", "Client", "Date", "Amount", "Invoice Status"]
    ws.append(headers)
    
    # Filter receipts by the user who created them
    receipts = Receipt.objects.filter(created_by=request.user).select_related('invoice')
    
    for receipt in receipts:
        ws.append([
            receipt.receipt_no,
            receipt.client_name,
            receipt.date_received.strftime("%Y-%m-%d"),
            receipt.amount_received,
            receipt.invoice.get_status_display(),
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=receipts.xlsx'
    wb.save(response)
    return response

@login_required
def export_pdf(request):
    receipts = get_filtered_receipts(request)
    company_logo_base64 = None
    try:
        company_profile = CompanyProfile.objects.get(user=request.user)
        if company_profile.logo and hasattr(company_profile.logo, 'path') and os.path.isfile(company_profile.logo.path):
            try:
                with open(company_profile.logo.path, 'rb') as img_file:
                    company_logo_base64 = 'data:image/png;base64,' + base64.b64encode(img_file.read()).decode('utf-8')
            except Exception as e:
                company_logo_base64 = None
        else:
            company_logo_base64 = None
    except CompanyProfile.DoesNotExist:
        company_profile = None
        company_logo_base64 = None
    
    # Get company context for currency
    company_context = get_company_context(request.user)
    
    context = {
        'receipts': receipts.order_by('-date_received', '-created_at'),
        'company_profile': company_profile,
        'company_logo_base64': company_logo_base64,
        'user_currency_symbol': company_context['currency_symbol'],
        'user_currency_code': company_context['currency_code'],
    }
    
    html_string = render_to_string('receipts/receipt_list_export_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=receipts.pdf'
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response
