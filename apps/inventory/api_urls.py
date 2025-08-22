from django.urls import path
from . import views

app_name = 'inventory_api'

urlpatterns = [
    # Basic inventory endpoints
    path('items/', views.inventory_list, name='item_list'),
    path('items/<int:pk>/', views.inventory_detail, name='item_detail'),
    
    # Layout endpoints
    path('layouts/', views.layout_list, name='layout_list'),
    path('layouts/<int:pk>/', views.layout_detail, name='layout_detail'),
    
    # AJAX endpoints
    path('ajax/update-field/', views.ajax_update_field, name='ajax_update_field'),
    path('ajax/update-status/', views.ajax_update_status, name='ajax_update_status'),
    path('ajax/stock-adjustment/', views.ajax_stock_adjustment, name='ajax_stock_adjustment'),
]
