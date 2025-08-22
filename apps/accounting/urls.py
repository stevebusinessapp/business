from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    # Dashboard and main views
    path('', views.accounting_dashboard, name='dashboard'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('ledger/', views.ledger_summary, name='ledger_summary'),
    
    # Transaction management
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/<uuid:transaction_id>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transactions/<uuid:transaction_id>/delete/', views.delete_transaction, name='delete_transaction'),
    path('transactions/<uuid:transaction_id>/reconcile/', views.reconcile_transaction, name='reconcile_transaction'),
    path('transactions/<uuid:transaction_id>/unreconcile/', views.unreconcile_transaction, name='unreconcile_transaction'),
    path('transactions/update_currencies/', views.update_transaction_currencies, name='update_transaction_currencies'),
    
    # Export and reports
    path('export/', views.export_accounting_data, name='export_data'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/<int:report_id>/', views.view_report, name='view_report'),
    path('reports/<int:report_id>/export-pdf/', views.export_report_pdf, name='export_report_pdf'),
    
    # Sync and utilities
    path('sync/', views.sync_from_other_apps, name='sync_from_other_apps'),
    
    # AJAX endpoints
    path('ajax/update-ledger/', views.update_ledger_ajax, name='update_ledger_ajax'),
    path('ajax/update-currency/', views.update_accounting_currency, name='update_accounting_currency'),
]
