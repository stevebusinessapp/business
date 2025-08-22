from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.inventory_dashboard, name='dashboard'),
    
    # Main inventory management
    path('list/', views.inventory_list, name='list'),
    path('create/', views.inventory_create, name='create'),
    path('update/<int:pk>/', views.inventory_update, name='update'),
    path('delete/<int:pk>/', views.inventory_delete, name='delete'),
    path('detail/<int:pk>/', views.inventory_detail, name='detail'),
    path('print/<int:pk>/', views.inventory_print, name='print'),
    
    # Layout management
    path('layouts/', views.layout_list, name='layout_list'),
    path('layouts/create/', views.layout_create, name='layout_create'),
    path('layouts/update/<int:pk>/', views.layout_update, name='layout_update'),
    path('layouts/delete/<int:pk>/', views.layout_delete, name='layout_delete'),
    path('layouts/detail/<int:pk>/', views.layout_detail, name='layout_detail'),
    
    # Template management
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/update/<int:pk>/', views.template_update, name='template_update'),
    path('templates/delete/<int:pk>/', views.template_delete, name='template_delete'),
    path('templates/detail/<int:pk>/', views.template_detail, name='template_detail'),
    
    # AJAX endpoints for real-time updates
    path('ajax/update-field/', views.ajax_update_field, name='ajax_update_field'),
    path('ajax/update-status/', views.ajax_update_status, name='ajax_update_status'),
    path('ajax/stock-adjustment/', views.ajax_stock_adjustment, name='ajax_stock_adjustment'),
    path('ajax/calculate-totals/', views.ajax_calculate_totals, name='ajax_calculate_totals'),
    path('ajax/bulk-update-status/', views.ajax_bulk_update_status, name='ajax_bulk_update_status'),
    path('ajax/bulk-delete/', views.ajax_bulk_delete, name='ajax_bulk_delete'),
    path('ajax/get-item-details/', views.ajax_get_item_details, name='ajax_get_item_details'),
    path('ajax/get-item-status/<int:pk>/', views.ajax_get_item_status, name='ajax_get_item_status'),
    path('ajax/quick-edit/', views.ajax_quick_edit, name='ajax_quick_edit'),
    path('ajax/save-layout/', views.ajax_save_layout, name='ajax_save_layout'),
    path('ajax/update-column-order/', views.ajax_update_column_order, name='ajax_update_column_order'),
    path('ajax/toggle-column-visibility/', views.ajax_toggle_column_visibility, name='ajax_toggle_column_visibility'),
    path('ajax/validate-field/', views.ajax_validate_field, name='ajax_validate_field'),
    path('ajax/get-calculation-preview/', views.ajax_get_calculation_preview, name='ajax_get_calculation_preview'),
    path('ajax/set-default-layout/', views.ajax_set_default_layout, name='ajax_set_default_layout'),
    path('ajax/layout-preview/', views.ajax_layout_preview, name='ajax_layout_preview'),
    path('ajax/update-currency/', views.update_inventory_currency, name='ajax_update_currency'),
    
    # Import/Export
    path('import/', views.inventory_import, name='import'),
    path('export/', views.inventory_export, name='export'),
    path('ajax/export-selected/', views.ajax_export_selected, name='ajax_export_selected'),
    path('ajax/export-preview/', views.ajax_export_preview, name='ajax_export_preview'),
    
    # Stock adjustments
    path('stock-adjustment/<int:pk>/', views.stock_adjustment, name='stock_adjustment'),
    
    # Custom field management
    path('custom-fields/', views.custom_field_list, name='custom_field_list'),
    path('custom-fields/create/', views.custom_field_create, name='custom_field_create'),
    path('custom-fields/update/<int:pk>/', views.custom_field_update, name='custom_field_update'),
    path('custom-fields/delete/<int:pk>/', views.custom_field_delete, name='custom_field_delete'),
    
    # Legacy URLs for backward compatibility
    path('products/', views.inventory_list, name='product_list'),  # Redirect to new list
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/update/<int:pk>/', views.category_update, name='category_update'),
]
