from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from .models import JobOrder, JobOrderComment, JobOrderLayout
from .forms import JobOrderForm, JobOrderCommentForm, JobOrderLayoutForm
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db import models
from decimal import Decimal
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import openpyxl
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import os
import urllib.parse
from apps.core.models import CompanyProfile
import base64

@login_required
def joborder_list(request):
    total_joborders = JobOrder.objects.count()
    # Show all job orders created by the current user
    joborders = JobOrder.objects.filter(created_by=request.user).order_by('-created_at')
    filtered_count = joborders.count()
    return render(request, 'job_orders/joborder_list.html', {'joborders': joborders, 'total_joborders': total_joborders, 'filtered_count': filtered_count})

@login_required
def joborder_detail(request, pk):
    joborder = get_object_or_404(JobOrder, pk=pk)
    # Only allow view if user is creator, org, or has can_view_all_joborders
    profile = getattr(request.user, 'profile', None)
    org = getattr(profile, 'organization', None) if profile else None
    if not (
        request.user == joborder.created_by or
        (org and joborder.organization == org) or
        request.user.has_perm('job_orders.can_view_all_joborders')
    ):
        raise PermissionDenied('You do not have permission to view this job order.')
    comments = joborder.comments.select_related('user').order_by('created_at')
    comment_form = JobOrderCommentForm()
    return render(request, 'job_orders/joborder_detail.html', {'joborder': joborder, 'comments': comments, 'comment_form': comment_form})

@login_required
def joborder_create(request):
    profile = getattr(request.user, 'profile', None)
    org = getattr(profile, 'organization', None) if profile else None
    layouts = JobOrderLayout.objects.filter(user=request.user) | JobOrderLayout.objects.filter(organization=org)
    layout_data = [
        {
            'id': layout.id,
            'name': layout.name,
            'structure': layout.structure,
        }
        for layout in layouts
    ]
    if request.method == 'POST':
        layout_id = request.POST.get('layout')
        layout = get_object_or_404(JobOrderLayout, id=layout_id)
        form = JobOrderForm(request.POST, layout=layout)
        if form.is_valid():
            joborder = form.save(commit=False)
            joborder.layout = layout
            joborder.created_by = request.user
            joborder.organization = org
            # Only set joborder.data from the hidden input
            data_json = request.POST.get('data')
            try:
                data = json.loads(data_json)
                if isinstance(data, dict):
                    data = [data]
                elif not isinstance(data, list):
                    data = []
            except Exception:
                data = []
            # Ensure every row has both 'quantity_raw' and 'quantity'
            for row in data:
                if 'quantity_raw' in row:
                    qty_clean = ''.join([c for c in str(row['quantity_raw']) if c.isdigit() or c == '.'])
                    row['quantity'] = qty_clean
                elif 'quantity' in row:
                    row['quantity'] = str(row['quantity'])
            joborder.data = data
            # Auto-calculate summary (example: total)
            summary = {}
            total = 0
            for row in data:
                if 'quantity' in row and 'unit_price' in row:
                    try:
                        total += float(row['quantity']) * float(row['unit_price'])
                    except Exception:
                        pass
            if total:
                summary['total'] = total
            joborder.summary = summary
            joborder.save()
            messages.success(request, 'Job Order created successfully.')
            return redirect('job_orders:joborder_detail', pk=joborder.pk)
    else:
        layout = layouts.first() if layouts.exists() else None
        form = JobOrderForm(layout=layout)
    return render(request, 'job_orders/joborder_form.html', {'form': form, 'layouts': layouts, 'layout_data': layout_data})

@login_required
def joborder_edit(request, pk):
    joborder = get_object_or_404(JobOrder, pk=pk)
    if not joborder.is_editable():
        return render(request, 'job_orders/joborder_cannot_edit.html', {'joborder': joborder})
    layout = joborder.layout
    if request.method == 'POST':
        # Only validate title
        title = request.POST.get('title')
        if not title:
            messages.error(request, 'Title is required.')
        else:
            joborder.title = title
            # Only set joborder.data from the hidden input
            data_json = request.POST.get('data')
            try:
                data = json.loads(data_json)
                if isinstance(data, dict):
                    data = [data]
                elif not isinstance(data, list):
                    data = []
            except Exception:
                data = []
            # Ensure every row has both 'quantity_raw' and 'quantity'
            for row in data:
                if 'quantity_raw' in row:
                    qty_clean = ''.join([c for c in str(row['quantity_raw']) if c.isdigit() or c == '.'])
                    row['quantity'] = qty_clean
                elif 'quantity' in row:
                    row['quantity'] = str(row['quantity'])
            joborder.data = data
            # Auto-calculate summary (example: total)
            summary = {}
            total = 0
            for row in data:
                # Use quantity_raw if present, else quantity
                qty = row.get('quantity_raw', row.get('quantity', ''))
                qty_clean = ''.join([c for c in str(qty) if c.isdigit() or c == '.'])
                try:
                    qty_val = float(qty_clean) if qty_clean else 0
                except Exception:
                    qty_val = 0
                price_val = 0
                try:
                    price_val = float(row.get('unit_price', 0))
                except Exception:
                    pass
                total += qty_val * price_val
            if total:
                summary['total'] = total
            joborder.summary = summary
            joborder.save()
            messages.success(request, 'Job Order updated successfully.')
            return redirect('job_orders:joborder_detail', pk=joborder.pk)
    else:
        form = JobOrderForm(layout=layout, instance=joborder)
    # Pass joborder_data for JS initialization
    joborder_data = joborder.data
    if not isinstance(joborder_data, list):
        if isinstance(joborder_data, dict) and joborder_data:
            joborder_data = [joborder_data]
        else:
            joborder_data = []
    layouts = JobOrderLayout.objects.filter(models.Q(user=request.user) | models.Q(organization=joborder.organization))
    layout_data = [
        {
            'id': l.id,
            'name': l.name,
            'structure': l.structure,
        }
        for l in layouts
    ]
    return render(request, 'job_orders/joborder_form.html', {
        'form': form,
        'edit': True,
        'joborder': joborder,
        'joborder_data': joborder_data,
        'layouts': layouts,
        'layout_data': layout_data
    })

@login_required
def joborder_delete(request, pk):
    joborder = get_object_or_404(JobOrder, pk=pk)
    if request.method == 'POST':
        joborder.delete()
        messages.success(request, 'Job Order deleted.')
        return redirect('job_orders:joborder_list')
    return render(request, 'job_orders/joborder_confirm_delete.html', {'joborder': joborder})

@login_required
def joborder_submit(request, pk):
    joborder = get_object_or_404(JobOrder, pk=pk)
    if joborder.status == 'draft':
        joborder.status = 'submitted'
        joborder.save()
        messages.success(request, 'Job Order submitted for approval.')
    return redirect('job_orders:joborder_detail', pk=pk)

@login_required
def joborder_approve(request, pk):
    joborder = get_object_or_404(JobOrder, pk=pk)
    # Allow any authenticated user to approve their own job orders
    if not request.user.is_authenticated:
        return HttpResponseForbidden('You must be logged in to approve job orders.')
    # Optionally, restrict to only the creator
    if joborder.created_by != request.user:
        return HttpResponseForbidden('You can only approve your own job orders.')
    if joborder.status == 'pending':
        joborder.status = 'approved'
        joborder.approved_by = request.user
        joborder.approved_at = timezone.now()
        joborder.save()
        messages.success(request, 'Job Order approved.')
    return redirect('job_orders:joborder_detail', pk=pk)

@login_required
def joborder_reject(request, pk):
    joborder = get_object_or_404(JobOrder, pk=pk)
    if not request.user.has_perm('job_orders.can_approve_joborder'):
        return HttpResponseForbidden('You do not have permission to reject job orders.')
    if joborder.status == 'pending':
        joborder.status = 'rejected'
        joborder.approved_by = request.user
        joborder.approved_at = timezone.now()
        joborder.save()
        messages.success(request, 'Job Order rejected.')
    return redirect('job_orders:joborder_detail', pk=pk)

@login_required
def joborder_comment(request, pk):
    joborder = get_object_or_404(JobOrder, pk=pk)
    if request.method == 'POST':
        form = JobOrderCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.job_order = joborder
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added.')
    return redirect('job_orders:joborder_detail', pk=pk)

@login_required
def joborder_print(request, pk):
    joborder = get_object_or_404(JobOrder, pk=pk)
    return render(request, 'job_orders/joborder_print.html', {'joborder': joborder})

@login_required
def layout_list(request):
    layouts = JobOrderLayout.objects.filter(user=request.user) | JobOrderLayout.objects.filter(organization=getattr(getattr(request.user, 'profile', None), 'organization', None))
    return render(request, 'job_orders/layout_list.html', {'layouts': layouts})

@login_required
def layout_create(request):
    if request.method == 'POST':
        form = JobOrderLayoutForm(request.POST)
        if form.is_valid():
            layout = form.save(commit=False)
            layout.user = request.user
            profile = getattr(request.user, 'profile', None)
            layout.organization = getattr(profile, 'organization', None) if profile else None
            layout.save()
            messages.success(request, 'Layout created successfully.')
            return redirect('job_orders:layout_list')
    else:
        form = JobOrderLayoutForm()
    return render(request, 'job_orders/layout_form.html', {'form': form})

@login_required
def layout_edit(request, pk):
    layout = get_object_or_404(JobOrderLayout, pk=pk, user=request.user)
    old_structure = layout.structure.copy() if layout.structure else []
    if request.method == 'POST':
        form = JobOrderLayoutForm(request.POST, instance=layout)
        if form.is_valid():
            layout = form.save()
            new_structure = layout.structure
            old_names = {col['name']: col for col in old_structure}
            new_names = {col['name']: col for col in new_structure}
            # Find renamed, added, and removed columns
            removed = set(old_names) - set(new_names)
            added = set(new_names) - set(old_names)
            # For all job orders using this layout, update their data
            for joborder in layout.job_orders.all():
                updated = False
                for row in joborder.data:
                    # Remove deleted columns
                    for col in removed:
                        if col in row:
                            del row[col]
                            updated = True
                    # Add new columns
                    for col in added:
                        if col not in row:
                            row[col] = ''
                            updated = True
                    # For all columns in the structure, if missing, set to 'Not filled'
                    for col in new_names:
                        if col not in row:
                            row[col] = 'Not filled'
                            updated = True
                if updated:
                    joborder.save(update_fields=['data'])
            messages.success(request, 'Layout and all related job orders updated successfully.')
            return redirect('job_orders:layout_list')
    else:
        form = JobOrderLayoutForm(instance=layout)
    return render(request, 'job_orders/layout_form.html', {'form': form, 'edit': True})

@login_required
def layout_delete(request, pk):
    layout = get_object_or_404(JobOrderLayout, pk=pk, user=request.user)
    if request.method == 'POST':
        layout.delete()
        messages.success(request, 'Layout deleted.')
        return redirect('job_orders:layout_list')
    return render(request, 'job_orders/layout_confirm_delete.html', {'layout': layout})

@login_required
@csrf_exempt
def joborder_set_status(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
    joborder = get_object_or_404(JobOrder, pk=pk)
    if joborder.created_by != request.user:
        return JsonResponse({'success': False, 'error': 'You can only change status for your own job orders.'}, status=403)
    try:
        data = json.loads(request.body.decode('utf-8'))
        new_status = data.get('status')
        if new_status not in dict(JobOrder.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid status.'}, status=400)
        joborder.status = new_status
        if new_status == 'approved':
            joborder.approved_by = request.user
            joborder.approved_at = timezone.now()
        elif new_status == 'rejected':
            joborder.approved_by = request.user
            joborder.approved_at = timezone.now()
        else:
            joborder.approved_by = None
            joborder.approved_at = None
        joborder.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def export_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Job Orders"
    headers = ["Job Order #", "Title", "Status", "Created By", "Date"]
    ws.append(headers)
    for joborder in JobOrder.objects.filter(created_by=request.user):
        ws.append([
            joborder.tracking_id,
            joborder.title,
            joborder.get_status_display(),
            joborder.created_by.get_full_name() if joborder.created_by else '',
            joborder.created_at.strftime("%Y-%m-%d"),
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=joborders.xlsx'
    wb.save(response)
    return response

@login_required
def export_pdf(request):
    joborders = JobOrder.objects.filter(created_by=request.user)
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
    html_string = render_to_string('job_orders/joborder_list_export_pdf.html', {
        'joborders': joborders,
        'company_profile': company_profile,
        'company_logo_base64': company_logo_base64,
    })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=joborders.pdf'
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response
