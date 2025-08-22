from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import CompanyProfile, BankAccount
from .forms import CompanyProfileForm, BankAccountForm
from .utils import get_currency_info


def landing_page(request):
    """Landing page for non-authenticated users"""
    return render(request, 'core/landing_page.html')


@login_required
def dashboard(request):
    """Main dashboard view"""
    try:
        company_profile = request.user.company_profile
    except CompanyProfile.DoesNotExist:
        # Redirect to company profile creation if doesn't exist
        messages.warning(request, 'Please complete your company profile first.')
        return redirect('core:company_profile')
    
    context = {
        'company_profile': company_profile,
        'bank_accounts': company_profile.bank_accounts.all(),
        'total_bank_accounts': company_profile.bank_accounts.count(),
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def company_profile_view(request):
    """Company profile view and edit"""
    try:
        company_profile = request.user.company_profile
        created = False
    except CompanyProfile.DoesNotExist:
        company_profile = None
        created = True
    
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company_profile)
        if form.is_valid():
            # Delete old files if new ones are uploaded
            if company_profile and 'logo' in request.FILES:
                company_profile.delete_old_logo()
            if company_profile and 'signature' in request.FILES:
                company_profile.delete_old_signature()
            
            company_profile = form.save(commit=False)
            company_profile.user = request.user
            company_profile.save()
            
            if created:
                messages.success(request, 'Company profile created successfully!')
            else:
                messages.success(request, 'Company profile updated successfully!')
            
            return redirect('core:dashboard')
    else:
        form = CompanyProfileForm(instance=company_profile)
    
    context = {
        'form': form,
        'company_profile': company_profile,
        'created': created,
    }
    
    return render(request, 'core/company_profile.html', context)


@login_required
def bank_accounts_view(request):
    """Bank accounts management view"""
    try:
        company_profile = request.user.company_profile
    except CompanyProfile.DoesNotExist:
        messages.error(request, 'Please complete your company profile first.')
        return redirect('core:company_profile')
    
    bank_accounts = company_profile.bank_accounts.all()
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            bank_account = form.save(commit=False)
            bank_account.company = company_profile
            
            # Check if account number already exists for this company
            existing_account = BankAccount.objects.filter(
                company=company_profile,
                account_number=bank_account.account_number
            ).first()
            
            if existing_account:
                messages.error(request, f'A bank account with number {bank_account.account_number} already exists for your company.')
                return redirect('core:bank_accounts')
            
            try:
                bank_account.save()
                messages.success(request, 'Bank account added successfully!')
                return redirect('core:bank_accounts')
            except Exception as e:
                messages.error(request, 'Error saving bank account. Please try again.')
                return redirect('core:bank_accounts')
    else:
        form = BankAccountForm()
    
    context = {
        'form': form,
        'bank_accounts': bank_accounts,
        'company_profile': company_profile,
    }
    
    return render(request, 'core/bank_accounts.html', context)


@login_required
def edit_bank_account(request, pk):
    """Edit bank account"""
    bank_account = get_object_or_404(BankAccount, pk=pk, company__user=request.user)
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=bank_account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bank account updated successfully!')
            return redirect('core:bank_accounts')
    else:
        form = BankAccountForm(instance=bank_account)
    
    context = {
        'form': form,
        'bank_account': bank_account,
        'edit_mode': True,
    }
    
    return render(request, 'core/bank_account_form.html', context)


@login_required
def delete_bank_account(request, pk):
    """Delete bank account"""
    bank_account = get_object_or_404(BankAccount, pk=pk, company__user=request.user)
    
    if request.method == 'POST':
        bank_account.delete()
        messages.success(request, 'Bank account deleted successfully!')
        return redirect('core:bank_accounts')
    
    context = {
        'bank_account': bank_account,
    }
    
    return render(request, 'core/confirm_delete.html', context)


@login_required
@require_http_methods(["POST"])
def set_default_bank_account(request, pk):
    """Set default bank account via AJAX"""
    bank_account = get_object_or_404(BankAccount, pk=pk, company__user=request.user)
    
    # Update all accounts to not default, then set this one as default
    BankAccount.objects.filter(company=bank_account.company).update(is_default=False)
    bank_account.is_default = True
    bank_account.save()
    
    return JsonResponse({'success': True, 'message': 'Default bank account updated successfully!'})


@csrf_exempt
@require_http_methods(["POST"])
def update_currency(request):
    """Update company currency settings"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    try:
        # Parse JSON data
        data = json.loads(request.body)
        currency_code = data.get('currency_code')
        
        if not currency_code:
            return JsonResponse({'success': False, 'error': 'Currency code is required'})
        
        # Validate currency code
        currency_info = get_currency_info(currency_code)
        if not currency_info:
            return JsonResponse({'success': False, 'error': f'Invalid currency code: {currency_code}'})
        
        # Get company profile
        try:
            company_profile = request.user.company_profile
        except CompanyProfile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Company profile not found. Please complete your company profile first.'})
        
        # Store old currency for comparison
        old_currency = company_profile.currency_symbol
        
        # Update company profile currency
        company_profile.currency_code = currency_code
        company_profile.currency_symbol = currency_info['symbol']
        company_profile.save()
        
        # Update accounting transactions if currency changed
        transactions_updated = 0
        if old_currency != currency_info['symbol']:
            try:
                from apps.accounting.models import Transaction
                # Update all transactions for this company
                transactions_updated = Transaction.objects.filter(
                    company=company_profile
                ).update(currency=currency_info['symbol'])
            except ImportError:
                # Accounting app might not be installed
                pass
            except Exception as transaction_error:
                # Log transaction update error but don't fail the currency update
                print(f"Warning: Failed to update transactions: {transaction_error}")
                pass
        
        return JsonResponse({
            'success': True,
            'currency_code': currency_code,
            'currency_symbol': currency_info['symbol'],
            'transactions_updated': transactions_updated,
            'message': f'Currency updated to {currency_code} ({currency_info["symbol"]}). {transactions_updated} transactions updated.'
        })
        
    except json.JSONDecodeError as e:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data provided'})
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Currency update error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': f'Failed to update currency: {str(e)}'})
