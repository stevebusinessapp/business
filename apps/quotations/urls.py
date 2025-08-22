from django.urls import path
from . import views

app_name = 'quotations'

urlpatterns = [
    # Main quotation views
    path('', views.quotation_list, name='quotation_list'),
    path('create/', views.quotation_create, name='quotation_create'),
    path('<int:pk>/', views.quotation_detail, name='quotation_detail'),
    path('<int:pk>/edit/', views.quotation_edit, name='quotation_edit'),
    path('<int:pk>/delete/', views.quotation_delete, name='quotation_delete'),
    path('<int:pk>/duplicate/', views.quotation_duplicate, name='quotation_duplicate'),
    path('<int:pk>/preview/', views.quotation_preview, name='quotation_preview'),
    
    # Export and print views
    path('<int:pk>/pdf/', views.quotation_pdf, name='quotation_pdf'),
    path('<int:pk>/print/', views.quotation_print, name='quotation_print'),
    path('export/excel/', views.quotation_export_excel, name='quotation_export_excel'),
    path('export/pdf/', views.quotation_export_pdf, name='quotation_export_pdf'),
    path('<int:pk>/export/excel/', views.quotation_export_excel, name='quotation_export_excel_single'),
    
    # Status and actions
    path('<int:pk>/update-status/', views.quotation_update_status, name='quotation_update_status'),
    path('<int:pk>/send-email/', views.quotation_send_email, name='quotation_send_email'),
    path('<int:pk>/convert-to-invoice/', views.convert_to_invoice, name='convert_to_invoice'),
    
    # AJAX endpoints
    path('<int:pk>/delete/ajax/', views.quotation_delete_ajax, name='quotation_delete_ajax'),
    path('bulk-actions/', views.quotation_bulk_actions, name='quotation_bulk_actions'),
    path('stats/', views.quotation_stats, name='quotation_stats'),
    
    # Template management
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:pk>/', views.template_detail, name='template_detail'),
    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
    path('templates/<int:pk>/duplicate/', views.template_duplicate, name='template_duplicate'),
    path('templates/<int:pk>/apply-to-all/', views.template_apply_to_all, name='template_apply_to_all'),
    
    # Debug and testing
    path('debug/', views.quotation_debug, name='quotation_debug'),
    path('test-create/', views.test_quotation_creation, name='test_quotation_creation'),
    path('test-simple/', views.test_simple_quotation, name='test_simple_quotation'),
    path('test-state/', views.test_quotation_state, name='test_quotation_state'),
    path('<int:pk>/debug/', views.debug_quotation, name='debug_quotation'),
    
    # API endpoints
    path('api/templates/', views.api_templates, name='api_templates'),
]
