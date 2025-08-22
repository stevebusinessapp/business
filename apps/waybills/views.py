from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from decimal import Decimal
import json
from .models import Waybill, WaybillItem, WaybillTemplate, WaybillFieldTemplate
from .forms import (
    DynamicWaybillForm, WaybillTemplateForm, WaybillFilterForm, 
    WaybillFieldTemplateForm, create_dynamic_item_form, BaseWaybillItemFormSet
)
import json
import openpyxl
from django.http import HttpResponse
from django.template.loader import render_to_string
# from weasyprint import HTML
from xhtml2pdf import pisa
import os
import urllib.parse
from apps.core.models import CompanyProfile
import base64


@login_required
def waybill_list(request):
    """List all waybills with filtering and pagination"""
    waybills = Waybill.objects.select_related('template', 'user').filter(user=request.user)
    filter_form = WaybillFilterForm(request.GET, user=request.user)
    
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        status = filter_form.cleaned_data.get('status')
        template = filter_form.cleaned_data.get('template')
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        
        if search:
            waybills = waybills.filter(
                Q(waybill_number__icontains=search) |
                Q(custom_data__icontains=search) |
                Q(notes__icontains=search)
            )
        
        if status:
            waybills = waybills.filter(status=status)
        
        if template:
            waybills = waybills.filter(template=template)
        
        if date_from:
            waybills = waybills.filter(waybill_date__gte=date_from)
        
        if date_to:
            waybills = waybills.filter(waybill_date__lte=date_to)
    
    # Pagination
    paginator = Paginator(waybills, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_waybills = waybills.count()
    pending_count = waybills.filter(status='pending').count()
    in_transit_count = waybills.filter(status='in_transit').count()
    delivered_count = waybills.filter(status='delivered').count()
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_waybills': total_waybills,
        'pending_count': pending_count,
        'in_transit_count': in_transit_count,
        'delivered_count': delivered_count,
    }
    return render(request, 'waybills/waybill_list.html', context)


def get_waybill_context(waybill, user):
    """Get context data for waybill rendering"""
    # Use cache for company profile data to avoid repeated queries
    cache_key = f'company_profile_{user.id}'
    cached_profile_data = cache.get(cache_key)
    
    if cached_profile_data:
        company_profile, company_logo, company_signature, default_bank_account = cached_profile_data
    else:
        # Get company profile data for display
        company_profile = None
        company_logo = None
        company_signature = None
        default_bank_account = None
        
        try:
            from apps.core.models import CompanyProfile, BankAccount
            
            # Optimize: Get company profile with prefetched bank accounts in one query
            company_profile = CompanyProfile.objects.select_related().get(user=user)
            
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
            
            # Cache the profile data for 5 minutes
            cache.set(cache_key, (company_profile, company_logo, company_signature, default_bank_account), 300)
                
        except Exception as e:
            pass
    
    # Get user account details
    user_profile = {
        'full_name': user.get_full_name(),
        'email': user.email,
        'phone': getattr(user, 'phone', None),
        'location': getattr(user, 'location', None),
        'website': getattr(user, 'website', None),
    }
    
    return {
        'waybill': waybill,
        'company_profile': company_profile,
        'company_logo': company_logo,
        'company_signature': company_signature,
        'default_bank_account': default_bank_account,
        'user_profile': user_profile,
    }


@login_required
def waybill_detail(request, pk):
    """View waybill details"""
    waybill = get_object_or_404(
        Waybill.objects.select_related('template', 'user').prefetch_related('items'), 
        pk=pk, user=request.user
    )
    context = get_waybill_context(waybill, request.user)
    return render(request, 'waybills/waybill_detail.html', context)


def waybill_create_minimal(request):
    """MINIMAL waybill create - NO FRILLS, GUARANTEED TO LOAD INSTANTLY"""
    
    # Check authentication
    if not request.user.is_authenticated:
        from django.http import HttpResponse
        return HttpResponse("""
        <!DOCTYPE html>
        <html><head><title>Login Required</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h2>Please Login First</h2>
            <p><a href="/auth/login/">Click here to login</a></p>
        </body></html>
        """)
    
    if request.method == 'POST':
        try:
            from .models import WaybillTemplate, Waybill, WaybillItem
            
            # Get or create template
            template, created = WaybillTemplate.objects.get_or_create(
                user=request.user,
                name="Default Waybill",
                defaults={'is_default': True}
            )
            
            # Create waybill
            waybill = Waybill.objects.create(
                user=request.user,
                template=template,
                status=request.POST.get('status', 'pending'),
                notes=request.POST.get('notes', ''),
                custom_data={
                    'sender_name': request.POST.get('sender_name', ''),
                    'receiver_name': request.POST.get('receiver_name', ''),
                    'destination': request.POST.get('destination', ''),
                }
            )
            
            # Success response
            from django.http import HttpResponse
            return HttpResponse(f"""
            <!DOCTYPE html>
            <html><head><title>Success</title></head>
            <body style="font-family: Arial; padding: 20px; background: #d4edda;">
                <h1 style="color: #155724;">✓ SUCCESS!</h1>
                <p>Waybill {waybill.waybill_number} created successfully!</p>
                <p><a href="/waybills/create/">Create Another</a> | <a href="/waybills/">View All</a></p>
            </body></html>
            """)
            
        except Exception as e:
            from django.http import HttpResponse
            return HttpResponse(f"""
            <!DOCTYPE html>
            <html><head><title>Error</title></head>
            <body style="font-family: Arial; padding: 20px; background: #f8d7da;">
                <h2 style="color: #721c24;">Error</h2>
                <p>{str(e)}</p>
                <p><a href="/waybills/create/">Try Again</a></p>
            </body></html>
            """)
    
    # GET request - MINIMAL HTML that loads instantly
    from django.http import HttpResponse
    return HttpResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Create Waybill - WORKING</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; background: #f8f9fa; }}
            .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .success {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input, select, textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success">
                ✓ PAGE LOADED SUCCESSFULLY! User: {request.user.email}
            </div>
            
            <h1>Create Waybill</h1>
            
            <form method="POST">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', 'dummy')}">
                
                <div class="form-group">
                    <label>Sender Name *</label>
                    <input type="text" name="sender_name" required placeholder="Enter sender name">
                </div>
                
                <div class="form-group">
                    <label>Receiver Name *</label>
                    <input type="text" name="receiver_name" required placeholder="Enter receiver name">
                </div>
                
                <div class="form-group">
                    <label>Destination *</label>
                    <input type="text" name="destination" required placeholder="Enter destination">
                </div>
                
                <div class="form-group">
                    <label>Status</label>
                    <select name="status">
                        <option value="pending">Pending</option>
                        <option value="in_transit">In Transit</option>
                        <option value="delivered">Delivered</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Notes</label>
                    <textarea name="notes" rows="3" placeholder="Additional notes (optional)"></textarea>
                </div>
                
                <button type="submit">Create Waybill</button>
            </form>
            
            <p style="margin-top: 20px; font-size: 12px; color: #666;">
                Time loaded: <script>document.write(new Date());</script>
            </p>
        </div>
    </body>
    </html>
    """)


@login_required
def waybill_create_simple(request):
    """SUPER SIMPLE waybill create - GUARANTEED TO WORK"""
    
    if request.method == 'POST':
        # Handle form submission
        from .models import WaybillTemplate, Waybill, WaybillItem
        
        template_id = request.POST.get('template_id')
        try:
            selected_template = WaybillTemplate.objects.get(id=template_id, user=request.user)
        except:
            selected_template = WaybillTemplate.objects.filter(user=request.user).first()
            if not selected_template:
                selected_template = WaybillTemplate.objects.create(
                    user=request.user,
                    name="Default Waybill",
                    is_default=True
                )
        
        # Create waybill
        waybill = Waybill.objects.create(
            user=request.user,
            template=selected_template,
            delivery_date=request.POST.get('delivery_date') or None,
            status=request.POST.get('status', 'pending'),
            notes=request.POST.get('notes', ''),
            custom_data={
                'sender_info': {
                    'sender_name': request.POST.get('custom_sender_info_sender_name', ''),
                    'sender_phone': request.POST.get('custom_sender_info_sender_phone', ''),
                },
                'receiver_info': {
                    'receiver_name': request.POST.get('custom_receiver_info_receiver_name', ''),
                    'receiver_phone': request.POST.get('custom_receiver_info_receiver_phone', ''),
                },
                'shipment_info': {
                    'destination': request.POST.get('custom_shipment_info_destination', ''),
                    'vehicle_number': request.POST.get('custom_shipment_info_vehicle_number', ''),
                }
            }
        )
        
        # Create items
        items_data = {}
        for key, value in request.POST.items():
            if key.startswith('items[') and '][' in key:
                item_index = key.split('[')[1].split(']')[0]
                field_name = key.split('[')[2].split(']')[0]
                if item_index not in items_data:
                    items_data[item_index] = {}
                items_data[item_index][field_name] = value
        
        for index, item_data in items_data.items():
            if any(value and str(value).strip() for value in item_data.values()):
                WaybillItem.objects.create(
                    waybill=waybill,
                    item_data=item_data,
                    row_order=int(index)
                )
        
        from django.contrib import messages
        messages.success(request, f'Waybill {waybill.waybill_number} created successfully!')
        return redirect('waybills:detail', pk=waybill.pk)
    
    # GET request - Simple template list
    from .models import WaybillTemplate
    templates = list(WaybillTemplate.objects.filter(user=request.user).only('id', 'name', 'is_default', 'primary_color', 'document_title')[:10])
    
    if not templates:
        templates = [WaybillTemplate.objects.create(
            user=request.user,
            name="Default Waybill",
            is_default=True
        )]
    
    selected_template = next((t for t in templates if t.is_default), templates[0])
    
    context = {
        'title': 'Create Waybill',
        'templates': templates,
        'selected_template': selected_template,
    }
    
    return render(request, 'waybills/bulletproof_create.html', context)


@login_required
def waybill_create_instant(request):
    """INSTANT LOAD waybill create - Loads in split second"""
    # ULTRA OPTIMIZATION: Load absolutely minimal data only
    
    if request.method == 'POST':
        # Handle form submission (same as before)
        selected_template_id = request.POST.get('template_id')
        try:
            selected_template = WaybillTemplate.objects.get(id=selected_template_id, user=request.user)
        except WaybillTemplate.DoesNotExist:
            # Get any template or create default
            selected_template = WaybillTemplate.objects.filter(user=request.user, is_default=True).first()
            if not selected_template:
                selected_template = WaybillTemplate.objects.filter(user=request.user).first()
                if not selected_template:
                    selected_template = WaybillTemplate.objects.create(
                        user=request.user,
                        name="Default Waybill",
                        is_default=True
                    )
        
        # Create waybill (simplified)
        waybill = Waybill(user=request.user, template=selected_template)
        waybill.delivery_date = request.POST.get('delivery_date') or None
        waybill.status = request.POST.get('status', 'pending')
        waybill.notes = request.POST.get('notes', '')
        
        # Simple custom data processing
        custom_data = {}
        for key, value in request.POST.items():
            if key.startswith('custom_'):
                custom_data[key] = value
            elif key.startswith('items['):
                # Handle items
                pass
        
        waybill.custom_data = custom_data
        waybill.save()
        
        # Process items quickly
        items_data = {}
        for key, value in request.POST.items():
            if key.startswith('items[') and '][' in key:
                item_index = key.split('[')[1].split(']')[0]
                field_name = key.split('[')[2].split(']')[0]
                if item_index not in items_data:
                    items_data[item_index] = {}
                items_data[item_index][field_name] = value
        
        for index, item_data in items_data.items():
            if any(value and str(value).strip() for value in item_data.values()):
                WaybillItem.objects.create(
                    waybill=waybill,
                    item_data=item_data,
                    row_order=int(index)
                )
        
        messages.success(request, f'Waybill {waybill.waybill_number} created successfully!')
        return redirect('waybills:detail', pk=waybill.pk)
    
    # GET request - INSTANT LOAD with minimal data
    # Only get essential template list - no DB relations, no heavy queries
    templates = list(WaybillTemplate.objects.filter(user=request.user).only(
        'id', 'name', 'is_default'
    ).order_by('-is_default', 'name')[:10])  # Limit to 10 templates max
    
    # Get or create minimal default template
    selected_template = next((t for t in templates if t.is_default), 
                           templates[0] if templates else None)
    
    if not selected_template:
        selected_template = WaybillTemplate.objects.create(
            user=request.user,
            name="Default",
            is_default=True
        )
    
    # Minimal context - NO company profile, NO heavy data
    context = {
        'title': 'Create Waybill',
        'templates': templates,
        'selected_template': selected_template,
    }
    
    return render(request, 'waybills/waybill_create_instant.html', context)


@login_required
def waybill_create_test(request):
    """MINIMAL TEST VIEW - NO COMPLEX LOGIC"""
    from django.http import HttpResponse
    import time
    
    start_time = time.time()
    print(f"[DEBUG] View started at {start_time}")
    
    try:
        print(f"[DEBUG] User: {request.user}")
        
        # Test 1: Simple HTTP response
        if request.GET.get('test') == '1':
            return HttpResponse(f"""
            <h1>✅ TEST 1 PASSED - Basic HTTP Response Works</h1>
            <p>Time: {time.time() - start_time:.3f}s</p>
            <p><a href="?test=2">Test 2: Template Rendering</a></p>
            """)
        
        # Test 2: Simple template rendering
        if request.GET.get('test') == '2':
            print(f"[DEBUG] Testing template rendering...")
            return render(request, 'waybills/waybill_test_simple.html', {
                'templates': [],
                'selected_template': None,
            })
        
        # Test 3: Database query
        if request.GET.get('test') == '3':
            print(f"[DEBUG] Testing database queries...")
            from .models import WaybillTemplate
            templates = list(WaybillTemplate.objects.filter(user=request.user)[:5])
            print(f"[DEBUG] Found {len(templates)} templates")
            return render(request, 'waybills/waybill_test_simple.html', {
                'templates': templates,
                'selected_template': templates[0] if templates else None,
            })
        
        # Default: Show test menu
        return HttpResponse(f"""
        <h1>🔍 WAYBILL DEBUG MENU</h1>
        <p>Choose a test to isolate the issue:</p>
        <ul>
            <li><a href="?test=1">Test 1: Basic HTTP Response</a></li>
            <li><a href="?test=2">Test 2: Template Rendering</a></li>
            <li><a href="?test=3">Test 3: Database Queries</a></li>
            <li><a href="/waybills/create-original/">Test 4: Original View</a></li>
        </ul>
        <p>Time: {time.time() - start_time:.3f}s</p>
        """)
        
    except Exception as e:
        print(f"[ERROR] Exception in test view: {e}")
        return HttpResponse(f"<h1>❌ ERROR: {e}</h1>")

@login_required
def waybill_create(request):
    """Create new waybill with dynamic preview - ULTRA OPTIMIZED"""
    # PERFORMANCE OPTIMIZATION 1: Aggressive caching with longer TTL
    cache_key = f'waybill_templates_v2_{request.user.id}'
    templates = cache.get(cache_key)
    
    if templates is None:
        # Optimized query: only fetch essential fields, use defer for heavy fields
        templates = list(WaybillTemplate.objects.filter(user=request.user).only(
            'id', 'name', 'is_default', 'primary_color', 'secondary_color'
        ).order_by('-is_default', 'name'))
        cache.set(cache_key, templates, 1800)  # Cache for 30 minutes
    
    # PERFORMANCE OPTIMIZATION 2: Default template with persistent caching
    default_template_cache_key = f'default_waybill_template_v2_{request.user.id}'
    default_template = cache.get(default_template_cache_key)
    
    if default_template is None:
        if not templates:
            # Create default template with minimal required fields
            default_template = WaybillTemplate.objects.create(
                user=request.user,
                name="Default Waybill",
                description="Default waybill template",
                is_default=True,
                primary_color='#FF5900',
                secondary_color='#f8f9fa'
            )
            templates = [default_template]
            cache.set(cache_key, templates, 1800)
        else:
            default_template = next((t for t in templates if t.is_default), templates[0] if templates else None)
        
        if default_template:
            cache.set(default_template_cache_key, default_template, 1800)
    
    # PERFORMANCE OPTIMIZATION 3: Lazy template loading
    template_id = request.GET.get('template_id') or (default_template.id if default_template else None)
    selected_template = default_template  # Use cached default by default
    
    if template_id and str(template_id) != str(default_template.id if default_template else None):
        # Only query if different from default
        template_detail_cache_key = f'waybill_template_detail_{template_id}_{request.user.id}'
        selected_template = cache.get(template_detail_cache_key)
        
        if selected_template is None:
            try:
                selected_template = WaybillTemplate.objects.only(
                    'id', 'name', 'primary_color', 'secondary_color', 'custom_fields', 'table_columns'
                ).get(id=template_id, user=request.user)
                cache.set(template_detail_cache_key, selected_template, 1800)
            except WaybillTemplate.DoesNotExist:
                selected_template = default_template
    
    if request.method == 'POST':
        # Handle dynamic form data
        waybill = Waybill(user=request.user, template=selected_template)
        
        # Set basic waybill fields
        delivery_date = request.POST.get('delivery_date')
        waybill.delivery_date = delivery_date if delivery_date and delivery_date.strip() else None
        waybill.status = request.POST.get('status', 'pending')
        waybill.notes = request.POST.get('notes', '')
        
        # Process custom field data
        custom_data = {}
        custom_fields = selected_template.get_default_custom_fields()
        
        for section_key, section_config in custom_fields.items():
            if section_config.get('type') == 'section':
                custom_data[section_key] = {}
                for field_key, field_config in section_config.get('fields', {}).items():
                    field_name = f"custom_{section_key}_{field_key}"
                    custom_data[section_key][field_key] = request.POST.get(field_name, '')
        
        # Add user preferences to custom_data
        user_preferences = {
            'show_bank_details': request.POST.get('show-bank-details') == 'on',
            'show_company_details': request.POST.get('show-company-details') == 'on',
        }
        
        custom_data['user_preferences'] = user_preferences
        
        waybill.custom_data = custom_data
        
        # Save waybill first to get an ID
        waybill.save()
        
        # Process dynamic items - handle both formats
        items_data = {}
        
        # Check if items_data is sent as JSON (new format)
        if 'items_data' in request.POST:
            try:
                items_json = json.loads(request.POST.get('items_data', '[]'))
                for index, item_data in enumerate(items_json):
                    if any(value and str(value).strip() for value in item_data.values()):
                        items_data[str(index)] = item_data
            except json.JSONDecodeError:
                pass
        
        # Fallback to old format - collect all item data from POST
        if not items_data:
            for key, value in request.POST.items():
                if key.startswith('items[') and '][' in key:
                    # Parse items[1][description] format
                    item_index = key.split('[')[1].split(']')[0]
                    field_name = key.split('[')[2].split(']')[0]
                    
                    if item_index not in items_data:
                        items_data[item_index] = {}
                    items_data[item_index][field_name] = value
        
        # Create waybill items
        created_items = []
        for index, item_data in items_data.items():
            # Check if item has any meaningful data
            has_data = any(value and str(value).strip() for value in item_data.values())
            
            if has_data:
                item = WaybillItem.objects.create(
                    waybill=waybill,
                    item_data=item_data,
                    row_order=int(index) if index.isdigit() else 0
                )
                created_items.append(item)
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({
                'success': True,
                'message': f'Waybill {waybill.waybill_number} created successfully!',
                'waybill_id': waybill.pk,
                'waybill_number': waybill.waybill_number,
                'redirect_url': f'/waybills/{waybill.pk}/'
            })
        else:
            messages.success(request, f'Waybill {waybill.waybill_number} created successfully!')
            return redirect('waybills:detail', pk=waybill.pk)
    
    # GET request - show the dynamic form
    # Load company profile and bank account data for the template
    company_profile = None
    company_logo = None
    default_bank_account = None
    
    try:
        from apps.core.models import CompanyProfile, BankAccount
        
        # Get company profile
        company_profile = CompanyProfile.objects.get(user=request.user)
        
        # Get default bank account
        default_bank_account = BankAccount.objects.filter(
            company=company_profile,
            is_default=True
        ).first()
        
        if not default_bank_account:
            default_bank_account = BankAccount.objects.filter(company=company_profile).first()
            
    except CompanyProfile.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error loading company data: {e}")
    
    context = {
        'title': 'Create Waybill',
        'templates': templates,
        'selected_template': selected_template,
        'default_template': selected_template,
        'company_profile': company_profile,
        'company_logo': company_logo,
        'default_bank_account': default_bank_account,
    }
    return render(request, 'waybills/waybill_create_fixed.html', context)


@login_required
def waybill_edit(request, pk):
    """Edit existing waybill"""
    waybill = get_object_or_404(
        Waybill.objects.select_related('template', 'user').prefetch_related(
            'items'  # Simplified prefetch
        ), 
        pk=pk, user=request.user
    )
    
    if request.method == 'POST':
        # Set basic waybill fields
        delivery_date = request.POST.get('delivery_date')
        waybill.delivery_date = delivery_date if delivery_date and delivery_date.strip() else None
        waybill.status = request.POST.get('status', waybill.status)
        waybill.notes = request.POST.get('notes', '')

        # Map flat form fields to nested custom_data structure
        custom_data = {}
        custom_data['sender_info'] = {
            'sender_name': request.POST.get('sender_name', ''),
            'sender_phone': request.POST.get('sender_phone', ''),
            'sender_address': request.POST.get('sender_address', ''),
        }
        custom_data['receiver_info'] = {
            'receiver_name': request.POST.get('receiver_name', ''),
            'receiver_phone': request.POST.get('receiver_phone', ''),
            'receiver_address': request.POST.get('receiver_address', ''),
        }
        custom_data['shipment_info'] = {
            'destination': request.POST.get('destination', ''),
            'vehicle_number': request.POST.get('vehicle_number', ''),
            'driver_name': request.POST.get('driver_name', ''),
            'driver_phone': request.POST.get('driver_phone', ''),
        }
        user_preferences = {
            'show_bank_details': request.POST.get('show-bank-details') == 'on',
            'show_company_details': request.POST.get('show-company-details') == 'on',
        }
        custom_data['user_preferences'] = user_preferences
        waybill.custom_data = custom_data
        waybill.save()
        
        # Clear existing items and recreate
        waybill.items.all().delete()
        
        # Process dynamic items
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
        
        # Create waybill items
        for index, item_data in items_data.items():
            # Check if item has any meaningful data
            has_data = any(value and str(value).strip() for value in item_data.values())
            
            if has_data:
                WaybillItem.objects.create(
                    waybill=waybill,
                    item_data=item_data,
                    row_order=int(index)
                )
        
        messages.success(request, f'Waybill {waybill.waybill_number} updated successfully!')
        return redirect('waybills:list')
    
    # GET request - show edit form
    context = get_waybill_context(waybill, request.user)
    
    # Add edit-specific context - use cache for templates
    template_cache_key = f'user_templates_{request.user.id}'
    templates = cache.get(template_cache_key)
    
    if templates is None:
        templates = list(WaybillTemplate.objects.filter(user=request.user))
        cache.set(template_cache_key, templates, 300)  # Cache for 5 minutes
    
    # Prepare robust form_data and existing_items for the template
    form_data = {
        'waybill_number': waybill.waybill_number or '',
        'delivery_date': waybill.delivery_date.strftime('%Y-%m-%d') if waybill.delivery_date else '',
        'status': waybill.status or '',
        'notes': waybill.notes or '',
        'custom_data': waybill.custom_data or {},
    }
    existing_items = [
        {'id': item.id, 'item_data': item.item_data or {}} for item in waybill.items.all()
    ]
    if not existing_items:
        existing_items = [{}]  # Always at least one row

    context.update({
        'title': f'Edit Waybill {waybill.waybill_number}',
        'edit_mode': True,
        'waybill': waybill,
        'selected_template': waybill.template,
        'templates': templates,
        'form_data': form_data,
        'existing_items': existing_items,
    })
    return render(request, 'waybills/waybill_create_dynamic.html', context)


@login_required
def waybill_delete(request, pk):
    """Delete waybill with confirmation"""
    waybill = get_object_or_404(Waybill, pk=pk, user=request.user)
    
    if request.method == 'POST':
        waybill_number = waybill.waybill_number
        waybill.delete()
        messages.success(request, f'Waybill {waybill_number} deleted successfully!')
        return redirect('waybills:list')
    
    context = {'waybill': waybill}
    return render(request, 'waybills/waybill_delete.html', context)


@login_required
def waybill_delete_ajax(request, pk):
    """AJAX delete waybill"""
    if request.method == 'POST':
        try:
            waybill = get_object_or_404(Waybill, pk=pk, user=request.user)
            waybill_number = waybill.waybill_number
            waybill.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Waybill {waybill_number} deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def waybill_print(request, pk):
    """Print-friendly waybill view"""
    waybill = get_object_or_404(Waybill, pk=pk, user=request.user)
    
    # Use the same context as the detail view
    context = get_waybill_context(waybill, request.user)
    
    return render(request, 'waybills/waybill_print.html', context)


@login_required
def template_list(request):
    """List user's waybill templates"""
    templates = WaybillTemplate.objects.filter(user=request.user)
    
    context = {
        'templates': templates,
    }
    return render(request, 'waybills/template_list.html', context)


@login_required
def template_create(request):
    """Create new waybill template"""
    if request.method == 'POST':
        form = WaybillTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.user = request.user
            template.save()
            messages.success(request, f'Template "{template.name}" created successfully!')
            return redirect('waybills:template_detail', pk=template.pk)
    else:
        form = WaybillTemplateForm()
    
    context = {
        'form': form,
        'title': 'Create Waybill Template',
    }
    return render(request, 'waybills/template_form.html', context)


@login_required
def template_edit(request, pk):
    """Edit waybill template"""
    template = get_object_or_404(WaybillTemplate, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = WaybillTemplateForm(request.POST, instance=template)
        if form.is_valid():
            template = form.save()
            messages.success(request, f'Template "{template.name}" updated successfully!')
            return redirect('waybills:template_detail', pk=template.pk)
    else:
        form = WaybillTemplateForm(instance=template)
    
    context = {
        'form': form,
        'template': template,
        'title': f'Edit Template: {template.name}',
    }
    return render(request, 'waybills/template_form.html', context)


@login_required
def template_detail(request, pk):
    """View template details and customize fields"""
    template = get_object_or_404(WaybillTemplate, pk=pk, user=request.user)
    
    context = {
        'template': template,
    }
    return render(request, 'waybills/template_detail.html', context)


@login_required
def template_delete(request, pk):
    """Delete template"""
    template = get_object_or_404(WaybillTemplate, pk=pk, user=request.user)
    
    if request.method == 'POST':
        template_name = template.name
        template.delete()
        messages.success(request, f'Template "{template_name}" deleted successfully!')
        return redirect('waybills:template_list')
    
    context = {'template': template}
    return render(request, 'waybills/template_delete.html', context)


@login_required
def template_duplicate(request, pk):
    """Duplicate template"""
    template = get_object_or_404(WaybillTemplate, pk=pk, user=request.user)
    
    # Create duplicate
    new_template = WaybillTemplate.objects.create(
        user=request.user,
        name=f"{template.name} (Copy)",
        description=template.description,
        primary_color=template.primary_color,
        secondary_color=template.secondary_color,
        text_color=template.text_color,
        custom_fields=template.custom_fields,
        table_columns=template.table_columns,
        show_company_logo=template.show_company_logo,
        show_company_details=template.show_company_details,
        show_bank_details=template.show_bank_details,
        show_signature=template.show_signature,
        document_title=template.document_title,
        number_prefix=template.number_prefix,
        is_default=False,
    )
    
    messages.success(request, f'Template duplicated as "{new_template.name}"!')
    return redirect('waybills:template_detail', pk=new_template.pk)


@login_required
def api_template_fields(request, pk):
    """API endpoint to get template field configuration"""
    template = get_object_or_404(WaybillTemplate, pk=pk, user=request.user)
    
    return JsonResponse({
        'custom_fields': template.get_default_custom_fields(),
        'table_columns': template.get_default_table_columns(),
        'colors': {
            'primary_color': template.primary_color,
            'secondary_color': template.secondary_color,
            'text_color': template.text_color,
        },
        'settings': {
            'document_title': template.document_title,
            'show_company_logo': template.show_company_logo,
            'show_company_details': template.show_company_details,
            'show_bank_details': template.show_bank_details,
            'show_signature': template.show_signature,
        }
    })


@login_required
def api_save_template_config(request, pk):
    """API endpoint to save template configuration"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    
    template = get_object_or_404(WaybillTemplate, pk=pk, user=request.user)
    
    try:
        data = json.loads(request.body)
        
        # Update custom fields if provided
        if 'custom_fields' in data:
            template.custom_fields = data['custom_fields']
        
        # Update table columns if provided
        if 'table_columns' in data:
            template.table_columns = data['table_columns']
        
        # Update colors if provided
        if 'colors' in data:
            colors = data['colors']
            template.primary_color = colors.get('primary_color', template.primary_color)
            template.secondary_color = colors.get('secondary_color', template.secondary_color)
            template.text_color = colors.get('text_color', template.text_color)
        
        template.save()
        
        return JsonResponse({'success': True, 'message': 'Template updated successfully!'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_form_content(request):
    """API endpoint to load form content dynamically - INSTANT"""
    template_id = request.GET.get('template_id')
    
    # Ultra-fast minimal response
    if not template_id:
        return HttpResponse('<input type="text" name="sender_name" class="form-control" placeholder="Sender Name"><input type="text" name="receiver_name" class="form-control" placeholder="Receiver Name">')
    
    # Get template with minimal data only
    try:
        template = WaybillTemplate.objects.only('id', 'name', 'primary_color').get(id=template_id, user=request.user)
        
        # Return minimal HTML directly - no template rendering for speed
        html = f'''
        <div style="background:#f8f9fa;padding:16px;border-radius:8px;border-left:4px solid {template.primary_color or "#e91e63"}">
            <h6 style="color:{template.primary_color or "#e91e63"};margin:0 0 12px 0">Sender Information</h6>
            <input type="text" name="custom_sender_info_sender_name" class="form-control" placeholder="Sender Name" required>
            <input type="text" name="custom_sender_info_sender_phone" class="form-control" placeholder="Sender Phone">
            <textarea name="custom_sender_info_sender_address" class="form-control" rows="2" placeholder="Sender Address"></textarea>
        </div>
        <div style="background:#f8f9fa;padding:16px;border-radius:8px;border-left:4px solid {template.primary_color or "#e91e63"};margin-top:15px">
            <h6 style="color:{template.primary_color or "#e91e63"};margin:0 0 12px 0">Receiver Information</h6>
            <input type="text" name="custom_receiver_info_receiver_name" class="form-control" placeholder="Receiver Name" required>
            <input type="text" name="custom_receiver_info_receiver_phone" class="form-control" placeholder="Receiver Phone">
            <textarea name="custom_receiver_info_receiver_address" class="form-control" rows="2" placeholder="Receiver Address"></textarea>
        </div>
        <div style="background:#f8f9fa;padding:16px;border-radius:8px;border-left:4px solid {template.primary_color or "#e91e63"};margin-top:15px">
            <h6 style="color:{template.primary_color or "#e91e63"};margin:0 0 12px 0">Shipment Details</h6>
            <input type="text" name="custom_shipment_info_destination" class="form-control" placeholder="Destination" required>
            <input type="text" name="custom_shipment_info_vehicle_number" class="form-control" placeholder="Vehicle Number">
            <input type="text" name="custom_shipment_info_driver_name" class="form-control" placeholder="Driver Name">
        </div>
        '''
        
        response = HttpResponse(html)
        response['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        return response
        
    except WaybillTemplate.DoesNotExist:
        return HttpResponse('<input type="text" name="sender_name" class="form-control" placeholder="Sender Name"><input type="text" name="receiver_name" class="form-control" placeholder="Receiver Name">')


@login_required
def api_preview_content(request):
    """API endpoint to load preview content dynamically - INSTANT"""
    template_id = request.GET.get('template_id')
    
    # Ultra-fast preview without complex queries
    try:
        template = WaybillTemplate.objects.only('id', 'name', 'primary_color', 'document_title').get(id=template_id, user=request.user)
        
        # Return minimal preview HTML directly
        html = f'''
        <div style="border:2px solid {template.primary_color or "#e91e63"};border-radius:12px;padding:24px;background:#fff;min-height:400px">
            <div style="text-align:center;margin-bottom:30px;border-bottom:3px solid {template.primary_color or "#e91e63"};padding-bottom:20px">
                <h2 style="color:{template.primary_color or "#e91e63"};margin:0;font-size:28px;font-weight:700">{template.document_title or "WAYBILL"}</h2>
                <div style="background:#f8f9fa;padding:8px 16px;margin-top:10px;display:inline-block;border-radius:20px">
                    <strong>WB-PREVIEW</strong>
                </div>
            </div>
            
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:25px">
                <div style="background:#f8f9fa;padding:16px;border-radius:8px;border-left:4px solid {template.primary_color or "#e91e63"}">
                    <h5 style="color:{template.primary_color or "#e91e63"};margin:0 0 12px 0;font-size:16px">From (Sender)</h5>
                    <div style="font-size:14px;color:#666">
                        <div><strong>Sample Sender Name</strong></div>
                        <div>+1 (555) 123-4567</div>
                        <div>123 Sender Street, City</div>
                    </div>
                </div>
                
                <div style="background:#f8f9fa;padding:16px;border-radius:8px;border-left:4px solid {template.primary_color or "#e91e63"}">
                    <h5 style="color:{template.primary_color or "#e91e63"};margin:0 0 12px 0;font-size:16px">To (Receiver)</h5>
                    <div style="font-size:14px;color:#666">
                        <div><strong>Sample Receiver Name</strong></div>
                        <div>+1 (555) 987-6543</div>
                        <div>456 Receiver Ave, City</div>
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom:25px">
                <h5 style="color:{template.primary_color or "#e91e63"};margin:0 0 12px 0;font-size:16px">Items</h5>
                <table style="width:100%;border-collapse:collapse;font-size:14px">
                    <thead>
                        <tr style="background:{template.primary_color or "#e91e63"};color:#fff">
                            <th style="padding:12px 8px;text-align:left;border:1px solid #ddd">Product</th>
                            <th style="padding:12px 8px;text-align:left;border:1px solid #ddd">Description</th>
                            <th style="padding:12px 8px;text-align:center;border:1px solid #ddd">Qty</th>
                            <th style="padding:12px 8px;text-align:center;border:1px solid #ddd">Weight</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding:10px 8px;border:1px solid #ddd">Electronics</td>
                            <td style="padding:10px 8px;border:1px solid #ddd">Sample electronic devices</td>
                            <td style="padding:10px 8px;border:1px solid #ddd;text-align:center">5</td>
                            <td style="padding:10px 8px;border:1px solid #ddd;text-align:center">2.5 kg</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div style="margin-top:30px;padding-top:20px;border-top:2px solid {template.primary_color or "#e91e63"};text-align:center;font-size:12px;color:#666">
                <div>Live preview of your waybill template</div>
            </div>
        </div>
        '''
        
        response = HttpResponse(html)
        response['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        return response
        
    except WaybillTemplate.DoesNotExist:
        return HttpResponse('<div style="border:2px solid #e91e63;border-radius:12px;padding:24px;text-align:center;min-height:400px;display:flex;align-items:center;justify-content:center"><div><h3 style="color:#e91e63">Select a Template</h3><p>Choose a template to see preview</p></div></div>')


@login_required 
def api_company_profile(request):
    """API endpoint to load company profile data lazily - ULTRA OPTIMIZED"""
    # PERFORMANCE OPTIMIZATION: Aggressive caching for company profile
    profile_cache_key = f'company_profile_optimized_{request.user.id}'
    cached_data = cache.get(profile_cache_key)
    
    if cached_data:
        return JsonResponse(cached_data)
    
    try:
        from apps.core.models import CompanyProfile, BankAccount
        
        # Single optimized query with select_related
        company_profile = CompanyProfile.objects.select_related('user').get(user=request.user)
        
        # Get default bank account in one query
        default_bank_account = BankAccount.objects.filter(
            company=company_profile, 
            is_default=True
        ).first() or BankAccount.objects.filter(company=company_profile).first()
        
        profile_data = {
            'success': True,
            'company_name': company_profile.company_name,
            'company_logo': company_profile.logo.url if company_profile.logo else None,
            'company_signature': company_profile.signature.url if company_profile.signature else None,
            'phone': company_profile.phone,
            'email': company_profile.email,
            'address': company_profile.address,
            'website': company_profile.website,
            'bank_account': {
                'bank_name': default_bank_account.bank_name,
                'account_name': default_bank_account.account_name,
                'account_number': default_bank_account.account_number,
            } if default_bank_account else None
        }
        
        # Cache for 1 hour
        cache.set(profile_cache_key, profile_data, 3600)
        
        return JsonResponse(profile_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def waybill_update_status(request, pk):
    """Update waybill status via AJAX"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            status = data.get('status')
            
            print(f"[DEBUG] Received status update request for waybill {pk}: {status}")
            
            # Validate status
            valid_statuses = ['delivered', 'pending', 'processing', 'dispatched', 'not_delivered', 'returned', 'cancelled', 'on_hold', 'awaiting_pickup']
            if status not in valid_statuses:
                print(f"[DEBUG] Invalid status received: {status}")
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                })
            
            # Get waybill
            waybill = get_object_or_404(Waybill, pk=pk, user=request.user)
            old_status = waybill.status
            
            print(f"[DEBUG] Waybill {pk} current status: {old_status}")
            
            # Update status
            waybill.status = status
            
            # Try to save and handle potential database issues
            try:
                waybill.save(update_fields=['status'])
                print(f"[DEBUG] Waybill {pk} save() completed")
            except Exception as save_error:
                print(f"[ERROR] Save failed: {save_error}")
                return JsonResponse({
                    'success': False,
                    'error': f'Database save failed: {str(save_error)}'
                })
            
            # Verify the save worked
            waybill.refresh_from_db()
            actual_status = waybill.status
            
            print(f"[DEBUG] Waybill {pk} status after save: {actual_status}")
            
            if actual_status != status:
                print(f"[ERROR] Status not saved correctly! Expected: {status}, Got: {actual_status}")
                
                # Check if this is a database schema issue
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT status FROM waybills_waybill WHERE id = %s", [pk])
                    db_status = cursor.fetchone()[0]
                    print(f"[DEBUG] Raw database status: {db_status}")
                
                # For now, let's try to force the update using raw SQL
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE waybills_waybill SET status = %s WHERE id = %s",
                            [status, pk]
                        )
                    
                    # Check if raw SQL worked
                    waybill.refresh_from_db()
                    if waybill.status == status:
                        print(f"[DEBUG] Raw SQL update worked for waybill {pk}")
                        return JsonResponse({
                            'success': True,
                            'message': f'Waybill status updated from {old_status} to {status} (via raw SQL)',
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
                'message': f'Waybill status updated from {old_status} to {status}',
                'old_status': old_status,
                'new_status': actual_status
            })
            
        except Exception as e:
            print(f"[ERROR] Exception in waybill_update_status: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def export_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Waybills"
    headers = ["Waybill #", "Sender", "Receiver", "Date", "Status"]
    ws.append(headers)
    for waybill in Waybill.objects.filter(user=request.user):
        ws.append([
            waybill.waybill_number,
            waybill.custom_data.get('sender_info', {}).get('sender_name', ''),
            waybill.custom_data.get('receiver_info', {}).get('receiver_name', ''),
            waybill.waybill_date.strftime("%Y-%m-%d"),
            waybill.get_status_display(),
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=waybills.xlsx'
    wb.save(response)
    return response

@login_required
def export_pdf(request):
    waybills = Waybill.objects.filter(user=request.user)
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
    html_string = render_to_string('waybills/waybill_list_export_pdf.html', {
        'waybills': waybills,
        'company_profile': company_profile,
        'company_logo_base64': company_logo_base64,
    })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=waybills.pdf'
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response
