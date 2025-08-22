from django.urls import path
from . import views

app_name = 'waybills'

urlpatterns = [
    # Waybill CRUD
    path('', views.waybill_list, name='list'),
    path('create/', views.waybill_create, name='create'),
    path('debug-test/', views.waybill_create_test, name='debug_test'),
    path('create-original/', views.waybill_create, name='create_original'),
    path('create-minimal/', views.waybill_create_minimal, name='create_minimal'),
    path('create-instant/', views.waybill_create_instant, name='create_instant'),
    path('<int:pk>/', views.waybill_detail, name='detail'),
    path('<int:pk>/edit/', views.waybill_edit, name='edit'),
    path('<int:pk>/delete/', views.waybill_delete, name='delete'),
    path('<int:pk>/delete-ajax/', views.waybill_delete_ajax, name='delete_ajax'),
    path('<int:pk>/print/', views.waybill_print, name='print'),
    path('<int:pk>/update-status/', views.waybill_update_status, name='update_status'),
    # Export endpoints
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    
    # Template management
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:pk>/', views.template_detail, name='template_detail'),
    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
    path('templates/<int:pk>/duplicate/', views.template_duplicate, name='template_duplicate'),
    
    # API endpoints
    path('api/templates/<int:pk>/fields/', views.api_template_fields, name='api_template_fields'),
    path('api/templates/<int:pk>/save/', views.api_save_template_config, name='api_save_template_config'),
    
    # Optimized lazy loading endpoints
    path('api/form-content/', views.api_form_content, name='api_form_content'),
    path('api/preview-content/', views.api_preview_content, name='api_preview_content'),
    path('api/company-profile/', views.api_company_profile, name='api_company_profile'),
]
