from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from decimal import Decimal
from .models import Invoice, InvoiceItem, InvoiceTemplate
from .forms import InvoiceForm, InvoiceItemFormSet, InvoiceFilterForm, InvoiceTemplateForm
# from apps.core.utils import generate_pdf_response
import openpyxl
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.http import HttpResponse
from apps.core.models import CompanyProfile
import os
import urllib.parse
import base64


def get_filtered_invoices(request):
    # CRITICAL SECURITY FIX: Filter invoices by user to prevent data leakage
    invoices = Invoice.objects.filter(user=request.user).select_related('user', 'template')
    filter_form = InvoiceFilterForm(request.GET)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        status = filter_form.cleaned_data.get('status')
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        if search:
            invoices = invoices.filter(
                Q(invoice_number__icontains=search) |
                Q(client_name__icontains=search) |
                Q(client_email__icontains=search) |
                Q(client_phone__icontains=search) |
                Q(notes__icontains=search)
            )
        if status:
            invoices = invoices.filter(status=status)
        if date_from:
            invoices = invoices.filter(invoice_date__gte=date_from)
        if date_to:
            invoices = invoices.filter(invoice_date__lte=date_to)
    return invoices

@login_required
def invoice_list(request):
    invoices = get_filtered_invoices(request)
    filter_form = InvoiceFilterForm(request.GET)
    paginator = Paginator(invoices, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    from django.db.models import Sum, Count
    totals = invoices.aggregate(
        total_count=Count('id'),
        total_amount=Sum('grand_total') or 0,
        paid_amount=Sum('amount_paid') or 0
    )
    current_template = InvoiceTemplate.objects.filter(user=request.user, is_default=True).first()
    if not current_template:
        current_template = InvoiceTemplate.objects.filter(user=request.user).first()
        if not current_template:
            current_template = InvoiceTemplate.objects.create(
                user=request.user,
                name="Default Invoice Template",
                description="Automatically created default template",
                is_default=True
            )
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_invoices': totals['total_count'],
        'total_amount': totals['total_amount'],
        'paid_amount': totals['paid_amount'],
        'current_template': current_template,
    }
    return render(request, 'invoices/invoice_list.html', context)


def get_invoice_context(invoice, user):
    """Get context data for invoice rendering"""
    # Get company profile data for display
    company_profile = None
    company_logo = None
    company_signature = None
    default_bank_account = None
    
    try:
        from apps.core.models import CompanyProfile, BankAccount
        company_profile = CompanyProfile.objects.get(user=user)
        
        if company_profile.logo:
            company_logo = company_profile.logo.url
        if company_profile.signature:
            company_signature = company_profile.signature.url
            
        # Get default bank account
        default_bank_account = BankAccount.objects.filter(
            company=company_profile, 
            is_default=True
        ).first()
        
        # If no default, get the first bank account
        if not default_bank_account:
            default_bank_account = BankAccount.objects.filter(
                company=company_profile
            ).first()
            
    except CompanyProfile.DoesNotExist:
        pass
    
    # Get user account details for receipts
    user_profile = {
        'full_name': user.get_full_name(),
        'email': user.email,
        'phone': getattr(user, 'phone', None),
        'location': getattr(user, 'location', None),
        'website': getattr(user, 'website', None),
    }
    
    # Get current default template for unified styling
    current_template = InvoiceTemplate.objects.filter(user=user, is_default=True).first()
    
    # Create a default template if user has none
    if not current_template:
        current_template = InvoiceTemplate.objects.filter(user=user).first()
        if not current_template:
            current_template = InvoiceTemplate.objects.create(
                user=user,
                name="Default Invoice Template",
                description="Automatically created default template",
                is_default=True
            )
    
    return {
        'invoice': invoice,
        'company_profile': company_profile,
        'company_logo': company_logo,
        'company_signature': company_signature,
        'default_bank_account': default_bank_account,
        'user_profile': user_profile,
        'current_template': current_template,  # Use current template instead of invoice.template
    }


@login_required
def invoice_detail(request, pk):
    """View invoice details"""
    invoice = get_object_or_404(
        Invoice.objects.select_related('user').prefetch_related('items'), 
        pk=pk, user=request.user
    )
    context = get_invoice_context(invoice, request.user)
    return render(request, 'invoices/invoice_detail.html', context)


@login_required
def invoice_create(request):
    """Create new invoice with dynamic preview"""
    if request.method == 'POST':
        # Handle dynamic form data
        invoice = Invoice(user=request.user)
        
        # Set basic invoice fields
        invoice.client_name = request.POST.get('client_name', '')
        invoice.client_email = request.POST.get('client_email', '')
        invoice.client_phone = request.POST.get('client_phone', '')
        invoice.client_address = request.POST.get('client_address', '')
        
        # Handle due_date - convert empty string to None for proper date handling
        due_date = request.POST.get('due_date')
        invoice.due_date = due_date if due_date and due_date.strip() else None
        
        invoice.notes = request.POST.get('notes', '')
        
        # Parse financial fields with smart number parsing
        tax_rate = Invoice.parse_number(request.POST.get('tax_rate', '0'))
        discount = Invoice.parse_number(request.POST.get('discount', '0'))
        shipping_fee = Invoice.parse_number(request.POST.get('shipping_fee', '0'))
        other_charges = Invoice.parse_number(request.POST.get('other_charges', '0'))
        amount_paid = Invoice.parse_number(request.POST.get('amount_paid', '0'))
        
        invoice._tax_rate = tax_rate  # Store for calculation
        invoice.total_discount = discount
        invoice.shipping_fee = shipping_fee
        invoice.other_charges = other_charges
        invoice.amount_paid = amount_paid
        
        # Handle template selection
        template_id = request.POST.get('template')
        if template_id:
            try:
                template = InvoiceTemplate.objects.get(id=template_id, user=request.user)
                invoice.template = template
            except InvoiceTemplate.DoesNotExist:
                pass
        else:
            # Use default template if no template selected
            default_template = InvoiceTemplate.objects.filter(user=request.user, is_default=True).first()
            if default_template:
                invoice.template = default_template
        
        # Save invoice first to get an ID
        invoice.save()
        
        # Process dynamic items
        subtotal = 0
        items_data = {}
        
        # Collect all item data from POST
        for key, value in request.POST.items():
            if key.startswith('items[') and '][' in key:
                # Parse items[1][description] format
                item_index = key.split('[')[1].split(']')[0]
                field_name = key.split('[')[2].split(']')[0]
                
                if item_index not in items_data:
                    items_data[item_index] = {}
                items_data[item_index][field_name] = value
        
        # Create invoice items
        created_items = []
        for index, item_data in items_data.items():
            # Get all item fields
            product_service = item_data.get('product_service', '').strip()
            description = item_data.get('description', '').strip()
            quantity = item_data.get('quantity', '').strip()
            unit_price = item_data.get('unit_price', '').strip()
            
            # Create item if we have quantity or price (even without description)
            if quantity or unit_price:
                print(f"DEBUG: Creating item - product_service: '{product_service}', description: '{description}', qty: '{quantity}', price: '{unit_price}'")
                
                # Ensure we save the text content properly
                parsed_quantity = Invoice.parse_number(quantity or '0')
                parsed_price = Invoice.parse_number(unit_price or '0')
                
                item = InvoiceItem.objects.create(
                    invoice=invoice,
                    product_service=product_service or '',
                    description=description or '',
                    quantity=Decimal(str(parsed_quantity)),
                    unit_price=parsed_price
                )
                subtotal += item.line_total
                
                print(f"DEBUG: Saved item - ID: {item.id}, product_service: '{item.product_service}', description: '{item.description}', qty: {item.quantity}, price: {item.unit_price}, total: {item.line_total}")
        
        # Update invoice with calculated subtotal and totals
        invoice.subtotal = subtotal
        invoice.calculate_totals()
        invoice.save()
        
        messages.success(request, f'Invoice {invoice.invoice_number} created successfully!')
        return redirect('invoices:detail', pk=invoice.pk)
    
    # GET request - show the dynamic form
    # Get company profile data
    company_profile = None
    company_logo = None
    
    try:
        from apps.core.models import CompanyProfile, BankAccount
        company_profile = CompanyProfile.objects.get(user=request.user)
        if company_profile.logo:
            company_logo = company_profile.logo.url
            
        # Get default bank account
        default_bank_account = BankAccount.objects.filter(
            company=company_profile, 
            is_default=True
        ).first()
        
        # If no default, get the first bank account
        if not default_bank_account:
            default_bank_account = BankAccount.objects.filter(
                company=company_profile
            ).first()
            
    except CompanyProfile.DoesNotExist:
        default_bank_account = None
    
    # Get user's invoice templates
    templates = InvoiceTemplate.objects.filter(user=request.user)
    default_template = templates.filter(is_default=True).first()
    
    # Create a default template if user has none
    if not templates.exists():
        default_template = InvoiceTemplate.objects.create(
            user=request.user,
            name="My First Invoice Template",
            description="Automatically created default template with standard colors",
            is_default=True
        )
        templates = InvoiceTemplate.objects.filter(user=request.user)
    
    context = {
        'title': 'Create Invoice',
        'company_profile': company_profile,
        'company_logo': company_logo,
        'default_bank_account': default_bank_account,
        'templates': templates,
        'default_template': default_template,
    }
    return render(request, 'invoices/invoice_create_dynamic.html', context)


@login_required
def invoice_edit(request, pk):
    """Edit existing invoice"""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    # Get company profile for currency settings
    try:
        company_profile = request.user.company_profile
    except:
        company_profile = None
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice, user=request.user)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        
        # Debug: Show what we received
        print(f"Form valid: {form.is_valid()}")
        print(f"Formset valid: {formset.is_valid()}")
        
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if not formset.is_valid():
            print(f"Formset errors: {formset.errors}")
            print(f"Formset non-form errors: {formset.non_form_errors()}")
        
        if form.is_valid() and formset.is_valid():
            # Save the main form first
            invoice = form.save()
            
            # Save formset to get items and deleted objects
            items = formset.save(commit=False)
            
            # Handle deleted objects (now available after save(commit=False))
            for item in formset.deleted_objects:
                print(f"Deleting item: {item.product_service} - ID: {item.id}")
                item.delete()
            
            # Save all valid items from formset
            valid_items = []
            
            for item in items:
                # Check if item has meaningful data
                has_product = bool(item.product_service and item.product_service.strip())
                has_description = bool(item.description and item.description.strip())
                has_quantity = item.quantity and item.quantity > 0
                has_price = item.unit_price and item.unit_price > 0
                
                if (has_product or has_description) and has_quantity and has_price:
                    item.invoice = invoice
                    item.save()
                    valid_items.append(item)
                    print(f"Saved item: {item.product_service} - Qty: {item.quantity} - Price: {item.unit_price} - Total: {item.line_total}")
                else:
                    print(f"Skipped empty item: product='{item.product_service}', qty={item.quantity}, price={item.unit_price}")
            
            print(f"Valid items saved: {len(valid_items)}")
            
            # Recalculate totals after all items are saved
            invoice.calculate_totals()
            invoice.save()
            
            print(f"Final invoice totals - Subtotal: {invoice.subtotal}, Grand Total: {invoice.grand_total}")
            
            messages.success(request, f'Invoice {invoice.invoice_number} updated successfully!')
            return redirect('invoices:detail', pk=invoice.pk)
        else:
            # Add error messages for debugging
            print("Form validation failed!")
            if not form.is_valid():
                print(f"Main form errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error in {field}: {error}')
            if not formset.is_valid():
                print(f"Formset errors: {formset.errors}")
                print(f"Formset non-form errors: {formset.non_form_errors()}")
                for i, form_errors in enumerate(formset.errors):
                    if form_errors:
                        for field, errors in form_errors.items():
                            for error in errors:
                                messages.error(request, f'Error in item {i+1} {field}: {error}')
                for error in formset.non_form_errors():
                    messages.error(request, f'Formset error: {error}')
    else:
        form = InvoiceForm(instance=invoice, user=request.user)
        formset = InvoiceItemFormSet(instance=invoice)
        
        # Debug: Show invoice data being loaded
        print(f"Loading invoice {invoice.invoice_number} with {invoice.items.count()} items")
        for item in invoice.items.all():
            print(f"  Item: {item.product_service} - Qty: {item.quantity} - Price: {item.unit_price}")
    
    # Debug: Print formset prefix for JavaScript (enabled for troubleshooting)
    print(f"Formset prefix: {formset.prefix}")
    print(f"Form fields: {list(form.fields.keys())}")
    print(f"Formset forms count: {len(formset.forms)}")
    
    # Debug: Show what's in the formset
    for i, form_instance in enumerate(formset.forms):
        if hasattr(form_instance, 'instance') and form_instance.instance.pk:
            print(f"  Formset form {i}: {form_instance.instance.product_service} (ID: {form_instance.instance.pk})")
    
    context = {
        'form': form,
        'formset': formset,
        'invoice': invoice,
        'title': f'Edit Invoice {invoice.invoice_number}',
        'company_profile': company_profile,
        'currency_symbol': company_profile.currency_symbol if company_profile else '₦',
        'formset_prefix': formset.prefix
    }
    return render(request, 'invoices/invoice_form.html', context)


@login_required
def invoice_delete(request, pk):
    """Delete invoice with confirmation"""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    if request.method == 'POST':
        invoice_number = invoice.invoice_number
        invoice.delete()
        messages.success(request, f'Invoice {invoice_number} deleted successfully!')
        return redirect('invoices:list')
    
    context = {'invoice': invoice}
    return render(request, 'invoices/invoice_delete.html', context)


@login_required
def invoice_delete_ajax(request, pk):
    """AJAX delete invoice"""
    if request.method == 'POST':
        try:
            invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
            invoice_number = invoice.invoice_number
            invoice.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Invoice {invoice_number} deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def invoice_pdf(request, pk):
    """Export invoice as PDF"""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    try:
        # Import xhtml2pdf for HTML to PDF conversion
        from xhtml2pdf import pisa
        from django.template.loader import render_to_string
        from io import BytesIO
        
        # Get the same context as the detail view
        context = get_invoice_context(invoice, request.user)
        
        # Build absolute URLs for images
        if context.get('company_logo'):
            context['company_logo'] = request.build_absolute_uri(context['company_logo'])
        if context.get('company_signature'):
            context['company_signature'] = request.build_absolute_uri(context['company_signature'])
            
        # Debug: Print context values
        print(f"PDF Context Debug:")
        print(f"Currency Symbol: {context.get('currency_symbol')}")
        print(f"Company Logo: {context.get('company_logo')}")
        print(f"Invoice Grand Total: {invoice.grand_total}")
        
        # Render HTML template
        html_string = render_to_string('invoices/invoice_pdf.html', context)
        
        # Create PDF from HTML
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        
        if not pdf.err:
            # Create response
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
            return response
        else:
            return HttpResponse("Error generating PDF", content_type="text/plain", status=500)
        
    except ImportError:
        # Fallback to old method if xhtml2pdf is not available
        return HttpResponse("xhtml2pdf is not installed. Please install it: pip install xhtml2pdf", 
                          content_type="text/plain", status=500)
    except Exception as e:
        # Handle any errors gracefully
        return HttpResponse(f"Error generating PDF: {str(e)}", content_type="text/plain", status=500)


@login_required
def invoice_print(request, pk):
    """Print-friendly invoice view"""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    # Use the same context as the detail and PDF views
    context = get_invoice_context(invoice, request.user)
    
    return render(request, 'invoices/invoice_print.html', context)


# ==============================================================================
# INVOICE TEMPLATE VIEWS
# ==============================================================================

@login_required
def template_list(request):
    """List user's invoice templates"""
    templates = InvoiceTemplate.objects.filter(user=request.user).select_related('user')
    
    context = {
        'templates': templates,
    }
    return render(request, 'invoices/template_list.html', context)


@login_required
def template_create(request):
    """Create new invoice template"""
    if request.method == 'POST':
        form = InvoiceTemplateForm(request.POST, user=request.user)
        if form.is_valid():
            template = form.save(commit=False)
            template.user = request.user
            
            # Check if template name already exists for this user
            if InvoiceTemplate.objects.filter(user=request.user, name=template.name).exists():
                form.add_error('name', f'You already have a template named "{template.name}". Please choose a different name.')
            else:
                try:
                    template.save()
                    messages.success(request, f'Template "{template.name}" created successfully!')
                    return redirect('invoices:template_detail', pk=template.pk)
                except Exception as e:
                    messages.error(request, f'Error creating template: {str(e)}')
    else:
        form = InvoiceTemplateForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create Invoice Template',
    }
    return render(request, 'invoices/template_form.html', context)


@login_required
def template_edit(request, pk):
    """Edit invoice template"""
    template = get_object_or_404(InvoiceTemplate, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = InvoiceTemplateForm(request.POST, instance=template, user=request.user)
        if form.is_valid():
            template = form.save()
            messages.success(request, f'Template "{template.name}" updated successfully!')
            
            # Update all existing invoices with this template to reflect color changes
            invoices_updated = Invoice.objects.filter(
                user=request.user, 
                template=template
            ).update(updated_at=template.updated_at)
            
            if invoices_updated > 0:
                messages.info(request, f'Color changes applied to {invoices_updated} existing invoices.')
            
            return redirect('invoices:template_detail', pk=template.pk)
    else:
        form = InvoiceTemplateForm(instance=template, user=request.user)
    
    context = {
        'form': form,
        'template': template,
        'title': f'Edit Template: {template.name}',
    }
    return render(request, 'invoices/template_form.html', context)


@login_required
def template_detail(request, pk):
    """View template details and preview"""
    template = get_object_or_404(InvoiceTemplate, pk=pk, user=request.user)
    
    # Count invoices using this template
    invoices_count = Invoice.objects.filter(template=template).count()
    
    context = {
        'template': template,
        'invoices_count': invoices_count,
    }
    return render(request, 'invoices/template_detail.html', context)


@login_required
def template_delete(request, pk):
    """Delete template"""
    template = get_object_or_404(InvoiceTemplate, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Check if any invoices use this template
        invoices_count = Invoice.objects.filter(template=template).count()
        
        if invoices_count > 0:
            messages.warning(request, f'Cannot delete template "{template.name}" - it is used by {invoices_count} invoices.')
            return redirect('invoices:template_detail', pk=template.pk)
        
        template_name = template.name
        template.delete()
        messages.success(request, f'Template "{template_name}" deleted successfully!')
        return redirect('invoices:template_list')
    
    context = {'template': template}
    return render(request, 'invoices/template_delete.html', context)


@login_required
def template_duplicate(request, pk):
    """Duplicate template"""
    template = get_object_or_404(InvoiceTemplate, pk=pk, user=request.user)
    
    # Create duplicate
    new_template = InvoiceTemplate.objects.create(
        user=request.user,
        name=f"{template.name} (Copy)",
        description=template.description,
        primary_color=template.primary_color,
        secondary_color=template.secondary_color,
        text_color=template.text_color,
        accent_color=template.accent_color,
        show_company_logo=template.show_company_logo,
        show_company_details=template.show_company_details,
        show_bank_details=template.show_bank_details,
        show_signature=template.show_signature,
        document_title=template.document_title,
        number_prefix=template.number_prefix,
        default_payment_terms=template.default_payment_terms,
        footer_text=template.footer_text,
        is_default=False  # Copy is never default
    )
    
    messages.success(request, f'Template duplicated as "{new_template.name}"!')
    return redirect('invoices:template_edit', pk=new_template.pk)


@login_required
def template_apply_to_all(request, pk):
    """Apply template colors to all user's invoices"""
    template = get_object_or_404(InvoiceTemplate, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Update all user's invoices to use this template
        invoices_updated = Invoice.objects.filter(user=request.user).update(
            template=template,
            updated_at=template.updated_at
        )
        
        messages.success(request, f'Applied template "{template.name}" to all {invoices_updated} invoices!')
        return redirect('invoices:template_detail', pk=template.pk)
    
    # Get count for confirmation
    total_invoices = Invoice.objects.filter(user=request.user).count()
    
    context = {
        'template': template,
        'total_invoices': total_invoices,
    }
    return render(request, 'invoices/template_apply_all.html', context)


@login_required
def api_templates(request):
    """API endpoint to get user's invoice templates"""
    if request.method == 'GET':
        templates = InvoiceTemplate.objects.filter(user=request.user).values(
            'id', 'name', 'primary_color', 'secondary_color', 
            'text_color', 'accent_color', 'is_default'
        )
        
        return JsonResponse({
            'templates': list(templates),
            'status': 'success'
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def invoice_update_status(request, pk):
    """Update invoice status via AJAX"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            status = data.get('status')
            
            print(f"[DEBUG] Received status update request for invoice {pk}: {status}")
            
            # Validate status
            valid_statuses = ['unpaid', 'partial', 'paid', 'delivered']
            if status not in valid_statuses:
                print(f"[DEBUG] Invalid status received: {status}")
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                })
            
            # Get invoice
            invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
            old_status = invoice.status
            
            print(f"[DEBUG] Invoice {pk} current status: {old_status}")
            
            # Update status
            invoice.status = status
            
            # Try to save and handle potential database issues
            try:
                invoice.save(update_fields=['status'])
                print(f"[DEBUG] Invoice {pk} save() completed")
            except Exception as save_error:
                print(f"[ERROR] Save failed: {save_error}")
                return JsonResponse({
                    'success': False,
                    'error': f'Database save failed: {str(save_error)}'
                })
            
            # Verify the save worked
            invoice.refresh_from_db()
            actual_status = invoice.status
            
            print(f"[DEBUG] Invoice {pk} status after save: {actual_status}")
            
            if actual_status != status:
                print(f"[ERROR] Status not saved correctly! Expected: {status}, Got: {actual_status}")
                
                # Check if this is a database schema issue
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT status FROM invoices_invoice WHERE id = %s", [pk])
                    db_status = cursor.fetchone()[0]
                    print(f"[DEBUG] Raw database status: {db_status}")
                
                # For now, let's try to force the update using raw SQL
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE invoices_invoice SET status = %s WHERE id = %s",
                            [status, pk]
                        )
                    
                    # Check if raw SQL worked
                    invoice.refresh_from_db()
                    if invoice.status == status:
                        print(f"[DEBUG] Raw SQL update worked for invoice {pk}")
                        return JsonResponse({
                            'success': True,
                            'message': f'Invoice status updated from {old_status} to {status} (via raw SQL)',
                            'old_status': old_status,
                            'new_status': status
                        })
                except Exception as sql_error:
                    print(f"[ERROR] Raw SQL update failed: {sql_error}")
                
                return JsonResponse({
                    'success': False,
                    'error': f'Status update failed. Expected "{status}", but database contains "{actual_status}". Database migration may be needed.'
                })
            
            return JsonResponse({
                'success': True,
                'message': f'Invoice status updated from {old_status} to {status}',
                'old_status': old_status,
                'new_status': actual_status
            })
            
        except Exception as e:
            print(f"[ERROR] Exception in invoice_update_status: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def invoice_toggle_payment(request, pk):
    """Toggle invoice payment status (for backward compatibility)"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            mark_as_paid = data.get('mark_as_paid', False)
            
            # Get invoice
            invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
            
            # Update status
            if mark_as_paid:
                invoice.status = 'paid'
            else:
                invoice.status = 'unpaid'
            
            invoice.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Invoice marked as {"paid" if mark_as_paid else "unpaid"}',
                'new_status': invoice.status
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def export_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Invoices"
    headers = ["Invoice #", "Client", "Date", "Due Date", "Amount", "Status"]
    ws.append(headers)
    for invoice in Invoice.objects.filter(user=request.user):
        ws.append([
            invoice.invoice_number,
            invoice.client_name,
            invoice.invoice_date.strftime("%Y-%m-%d"),
            invoice.due_date.strftime("%Y-%m-%d") if invoice.due_date else "",
            invoice.grand_total,
            invoice.get_status_display(),
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=invoices.xlsx'
    wb.save(response)
    return response

@login_required
def export_pdf(request):
    invoices = get_filtered_invoices(request)
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
    html_string = render_to_string('invoices/invoice_list_export_pdf.html', {
        'invoices': invoices,
        'company_profile': company_profile,
        'company_logo_base64': company_logo_base64,
    })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=invoices.pdf'
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response
