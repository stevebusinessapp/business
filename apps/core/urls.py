from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('landing/', views.landing_page, name='landing_page'),
    path('company-profile/', views.company_profile_view, name='company_profile'),
    path('bank-accounts/', views.bank_accounts_view, name='bank_accounts'),
    path('bank-accounts/<int:pk>/edit/', views.edit_bank_account, name='edit_bank_account'),
    path('bank-accounts/<int:pk>/delete/', views.delete_bank_account, name='delete_bank_account'),
    path('bank-accounts/<int:pk>/set-default/', views.set_default_bank_account, name='set_default_bank_account'),
    path('update-currency/', views.update_currency, name='update_currency'),
]
