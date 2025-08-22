from .models import CompanyProfile
from .utils import get_company_context


def company_context(request):
    """
    Context processor to make company data available in all templates
    
    Args:
        request: Django request object
    
    Returns:
        dict: Context data for templates
    """
    if request.user.is_authenticated:
        return get_company_context(request.user)
    
    return {
        'company_profile': None,
        'company_logo': None,
        'company_signature': None,
        'currency_symbol': '$',
        'currency_code': 'USD',
    }


def app_settings(request):
    """
    Context processor for general app settings
    
    Args:
        request: Django request object
    
    Returns:
        dict: App settings context
    """
    return {
        'app_name': 'Multi-Purpose Business App',
        'app_version': '1.0.0',
        'support_email': 'support@example.com',
        'max_file_upload_size': '5MB',
        'allowed_image_types': ['JPG', 'PNG', 'GIF', 'WebP'],
    }


def navigation_context(request):
    """
    Context processor for navigation data
    
    Args:
        request: Django request object
    
    Returns:
        dict: Navigation context
    """
    if not request.user.is_authenticated:
        return {}
    
    # Check if company profile exists
    has_company_profile = False
    try:
        has_company_profile = hasattr(request.user, 'company_profile') and request.user.company_profile is not None
    except CompanyProfile.DoesNotExist:
        pass
    
    navigation_items = [
        {
            'name': 'Dashboard',
            'url': 'core:dashboard',
            'icon': 'fas fa-tachometer-alt',
            'active': request.resolver_match.url_name == 'dashboard' if request.resolver_match else False
        },
        {
            'name': 'Company Profile',
            'url': 'core:company_profile',
            'icon': 'fas fa-building',
            'active': request.resolver_match.url_name in ['company_profile'] if request.resolver_match else False,
            'badge': 'Setup Required' if not has_company_profile else None,
            'badge_class': 'badge-warning' if not has_company_profile else None
        },
        {
            'name': 'Bank Accounts',
            'url': 'core:bank_accounts',
            'icon': 'fas fa-university',
            'active': request.resolver_match.url_name in ['bank_accounts', 'edit_bank_account'] if request.resolver_match else False
        },
    ]
    
    # Add other app navigation items if company profile exists
    if has_company_profile:
        additional_items = [
            {
                'name': 'Clients',
                'url': 'clients:client_list',
                'icon': 'fas fa-users',
                'active': request.resolver_match.namespace == 'clients' if request.resolver_match else False
            },
            {
                'name': 'Invoices',
                'url': 'invoices:invoice_list',
                'icon': 'fas fa-file-invoice',
                'active': request.resolver_match.namespace == 'invoices' if request.resolver_match else False
            },
            {
                'name': 'Quotations',
                'url': 'quotations:quotation_list',
                'icon': 'fas fa-file-contract',
                'active': request.resolver_match.namespace == 'quotations' if request.resolver_match else False
            },
            {
                'name': 'Receipts',
                'url': 'receipts:receipt_list',
                'icon': 'fas fa-receipt',
                'active': request.resolver_match.namespace == 'receipts' if request.resolver_match else False
            },
            {
                'name': 'Job Orders',
                'url': 'job_orders:job_order_list',
                'icon': 'fas fa-clipboard-list',
                'active': request.resolver_match.namespace == 'job_orders' if request.resolver_match else False
            },
            {
                'name': 'Waybills',
                'url': 'waybills:waybill_list',
                'icon': 'fas fa-truck',
                'active': request.resolver_match.namespace == 'waybills' if request.resolver_match else False
            },
            {
                'name': 'Expenses',
                'url': 'expenses:expense_list',
                'icon': 'fas fa-money-bill',
                'active': request.resolver_match.namespace == 'expenses' if request.resolver_match else False
            },
            {
                'name': 'Inventory',
                'url': 'inventory:dashboard',
                'icon': 'fas fa-boxes',
                'active': request.resolver_match.namespace == 'inventory' if request.resolver_match else False
            },
            {
                'name': 'Accounting',
                'url': 'accounting:dashboard',
                'icon': 'fas fa-calculator',
                'active': request.resolver_match.namespace == 'accounting' if request.resolver_match else False
            },
        ]
        navigation_items.extend(additional_items)
    
    return {
        'navigation_items': navigation_items,
        'has_company_profile': has_company_profile,
    }


def breadcrumb_context(request):
    """
    Context processor for breadcrumb navigation
    
    Args:
        request: Django request object
    
    Returns:
        dict: Breadcrumb context
    """
    breadcrumbs = [
        {'name': 'Home', 'url': 'core:dashboard'}
    ]
    
    if request.resolver_match:
        url_name = request.resolver_match.url_name
        namespace = request.resolver_match.namespace
        
        # Add breadcrumbs based on current page
        if namespace == 'core':
            if url_name == 'company_profile':
                breadcrumbs.append({'name': 'Company Profile', 'url': None})
            elif url_name in ['bank_accounts', 'edit_bank_account', 'delete_bank_account']:
                breadcrumbs.append({'name': 'Bank Accounts', 'url': 'core:bank_accounts'})
                if url_name == 'edit_bank_account':
                    breadcrumbs.append({'name': 'Edit', 'url': None})
                elif url_name == 'delete_bank_account':
                    breadcrumbs.append({'name': 'Delete', 'url': None})
        elif namespace == 'inventory':
            breadcrumbs.append({'name': 'Inventory', 'url': 'inventory:dashboard'})
            if url_name == 'dashboard':
                breadcrumbs.append({'name': 'Dashboard', 'url': None})
            elif url_name == 'inventory_list':
                breadcrumbs.append({'name': 'Products', 'url': None})
            elif url_name == 'inventory_create':
                breadcrumbs.append({'name': 'Add Product', 'url': None})
            elif url_name == 'inventory_update':
                breadcrumbs.append({'name': 'Edit Product', 'url': None})
            elif url_name == 'category_list':
                breadcrumbs.append({'name': 'Categories', 'url': None})
            elif url_name == 'custom_form_list':
                breadcrumbs.append({'name': 'Custom Forms', 'url': None})
            elif url_name == 'inventory_import':
                breadcrumbs.append({'name': 'Import', 'url': None})
            elif url_name == 'inventory_export':
                breadcrumbs.append({'name': 'Export', 'url': None})
    
    return {
        'breadcrumbs': breadcrumbs
    }


def user_preferences(request):
    """
    Context processor for user preferences and settings
    
    Args:
        request: Django request object
    
    Returns:
        dict: User preferences context
    """
    if not request.user.is_authenticated:
        return {}
    
    # Default preferences - can be extended with UserProfile model later
    preferences = {
        'theme': 'light',  # light, dark
        'sidebar_collapsed': False,
        'language': 'en',
        'timezone': 'UTC',
        'date_format': 'MM/DD/YYYY',
        'time_format': '12h',  # 12h, 24h
        'decimal_places': 2,
        'show_tooltips': True,
    }
    
    return {
        'user_preferences': preferences
    }


def currency_context(request):
    """
    Context processor to make currency information available globally
    """
    if request.user.is_authenticated:
        company_context = get_company_context(request.user)
        return {
            'user_currency_symbol': company_context['currency_symbol'],
            'user_currency_code': company_context['currency_code'],
            'company_profile': company_context['company_profile'],
        }
    else:
        return {
            'user_currency_symbol': '$',
            'user_currency_code': 'USD',
            'company_profile': None,
        }
