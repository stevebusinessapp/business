from django.urls import path
from . import views

app_name = 'job_orders'

urlpatterns = [
    path('', views.joborder_list, name='joborder_list'),
    path('create/', views.joborder_create, name='joborder_create'),
    path('<int:pk>/', views.joborder_detail, name='joborder_detail'),
    path('<int:pk>/edit/', views.joborder_edit, name='joborder_edit'),
    path('<int:pk>/delete/', views.joborder_delete, name='joborder_delete'),
    path('<int:pk>/submit/', views.joborder_submit, name='joborder_submit'),
    path('<int:pk>/approve/', views.joborder_approve, name='joborder_approve'),
    path('<int:pk>/reject/', views.joborder_reject, name='joborder_reject'),
    path('<int:pk>/comment/', views.joborder_comment, name='joborder_comment'),
    path('<int:pk>/print/', views.joborder_print, name='joborder_print'),
    path('<int:pk>/set_status/', views.joborder_set_status, name='joborder_set_status'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]

urlpatterns += [
    path('layouts/', views.layout_list, name='layout_list'),
    path('layouts/create/', views.layout_create, name='layout_create'),
    path('layouts/<int:pk>/edit/', views.layout_edit, name='layout_edit'),
    path('layouts/<int:pk>/delete/', views.layout_delete, name='layout_delete'),
]
