"""
URL configuration for business_app project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse

def health_check(request):
    """Health check endpoint for Render"""
    return HttpResponse("OK", status=200)

def simple_health(request):
    """Simple health check that always works"""
    return HttpResponse("healthy", content_type="text/plain")

urlpatterns = [
    path('healthz/', health_check, name='health_check'),
    path('health/', simple_health, name='simple_health'),
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/landing/', permanent=False)),
    path('auth/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.core.urls')),
    path('api/invoices/', include('apps.invoices.api_urls')),
    path('api/core/', include('apps.core.api_urls')),
    # path('api/receipts/', include('apps.receipts.api_urls')),
    # path('api/waybills/', include('apps.waybills.api_urls')),
    # path('api/job-orders/', include('apps.job_orders.api_urls')),
    path('quotations/', include(('apps.quotations.urls', 'quotations'), namespace='quotations')),
    # path('api/expenses/', include('apps.expenses.api_urls')),
    # path('api/inventory/', include('apps.inventory.api_urls')),
    path('api/clients/', include('apps.clients.api_urls')),
    path('api/inventory/', include('apps.inventory.api_urls')),
    # path('api/accounting/', include('apps.accounting.api_urls')),
    path('invoices/', include('apps.invoices.urls')),
    path('receipts/', include(('apps.receipts.urls', 'receipts'), namespace='receipts')),
    path('waybills/', include('apps.waybills.urls')),
    path('job-orders/', include(('apps.job_orders.urls', 'job_orders'), namespace='job_orders')),
    path('clients/', include(('apps.clients.urls', 'clients'), namespace='clients')),
    path('inventory/', include(('apps.inventory.urls', 'inventory'), namespace='inventory')),
    path('accounting/', include(('apps.accounting.urls', 'accounting'), namespace='accounting')),
    # path('expenses/', include('apps.expenses.urls')),
    # path('clients/', include('apps.clients.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Serve media files in production
    from django.views.static import serve
    from django.urls import re_path
    
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
