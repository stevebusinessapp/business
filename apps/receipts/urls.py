from django.urls import path
from . import views

app_name = 'receipts'

urlpatterns = [
    path('', views.receipt_list_view, name='list'),
    path('create/', views.receipt_create_view, name='create'),
    path('create/<int:invoice_id>/', views.receipt_create_view, name='create_from_invoice'),
    path('<int:receipt_id>/', views.receipt_detail_view, name='detail'),
    path('<int:receipt_id>/edit/', views.receipt_edit_view, name='edit'),
    path('<int:receipt_id>/delete/', views.receipt_delete_view, name='delete'),
    path('<int:receipt_id>/print/', views.receipt_print_view, name='print'),
    path('<int:receipt_id>/pdf/', views.receipt_pdf_view, name='pdf'),
    path('<int:receipt_id>/email/', views.receipt_email_view, name='email'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]
