from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.utils import timezone
from .models import Client
from .forms import ClientForm

@login_required
def client_list(request):
    """List all clients for the current user's company"""
    try:
        company_profile = request.user.company_profile
        if company_profile:
            clients = Client.objects.filter(company=company_profile)
            
            # Handle search
            search = request.GET.get('search', '')
            if search:
                clients = clients.filter(
                    models.Q(name__icontains=search) |
                    models.Q(email__icontains=search) |
                    models.Q(phone__icontains=search) |
                    models.Q(address__icontains=search)
                )
            
            # Handle sorting
            sort = request.GET.get('sort', 'name')
            if sort == '-name':
                clients = clients.order_by('-name')
            elif sort == 'created_at':
                clients = clients.order_by('created_at')
            elif sort == '-created_at':
                clients = clients.order_by('-created_at')
            else:
                clients = clients.order_by('name')
                
        else:
            clients = Client.objects.none()
    except:
        clients = Client.objects.none()
    
    # Calculate statistics
    total_clients = clients.count()
    active_clients = clients.filter(created_at__gte=timezone.now() - timezone.timedelta(days=30)).count()
    recent_clients = clients.filter(created_at__gte=timezone.now() - timezone.timedelta(days=30)).count()
    
    # Get total quotations for this company
    from apps.quotations.models import Quotation
    total_quotations = Quotation.objects.filter(user=request.user).count()
    
    return render(request, 'clients/client_list.html', {
        'clients': clients,
        'total_clients': total_clients,
        'active_clients_count': active_clients,
        'recent_clients_count': recent_clients,
        'total_quotations': total_quotations,
    })

@login_required
def client_create(request):
    """Create a new client"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            try:
                client.company = request.user.company_profile
                client.created_by = request.user
            except:
                messages.error(request, 'Please create a company profile first.')
                return redirect('core:company_profile')
            client.save()
            messages.success(request, f'Client "{client.name}" created successfully!')
            return redirect('clients:client_list')
    else:
        form = ClientForm()
    
    return render(request, 'clients/client_form.html', {
        'form': form,
        'create': True
    })

@login_required
def client_detail(request, pk):
    """View client details"""
    try:
        company_profile = request.user.company_profile
        if company_profile:
            client = get_object_or_404(Client, pk=pk, company=company_profile)
        else:
            messages.error(request, 'Please create a company profile first.')
            return redirect('core:company_profile')
    except:
        messages.error(request, 'Client not found.')
        return redirect('clients:client_list')
    
    return render(request, 'clients/client_detail.html', {
        'client': client
    })

@login_required
def client_edit(request, pk):
    """Edit client"""
    try:
        company_profile = request.user.company_profile
        if company_profile:
            client = get_object_or_404(Client, pk=pk, company=company_profile)
        else:
            messages.error(request, 'Please create a company profile first.')
            return redirect('core:company_profile')
    except:
        messages.error(request, 'Client not found.')
        return redirect('clients:client_list')
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client "{client.name}" updated successfully!')
            return redirect('clients:client_detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'clients/client_form.html', {
        'form': form,
        'client': client,
        'create': False
    })

@login_required
def client_delete(request, pk):
    """Delete client"""
    try:
        company_profile = request.user.company_profile
        if company_profile:
            client = get_object_or_404(Client, pk=pk, company=company_profile)
        else:
            messages.error(request, 'Please create a company profile first.')
            return redirect('core:company_profile')
    except:
        messages.error(request, 'Client not found.')
        return redirect('clients:client_list')
    
    if request.method == 'POST':
        client_name = client.name
        client.delete()
        messages.success(request, f'Client "{client_name}" deleted successfully!')
        return redirect('clients:client_list')
    
    return render(request, 'clients/client_confirm_delete.html', {
        'client': client
    })
