from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'core_api'

router = DefaultRouter()
router.register(r'company-profiles', api_views.CompanyProfileViewSet, basename='companyprofile')
router.register(r'bank-accounts', api_views.BankAccountViewSet, basename='bankaccount')

urlpatterns = [
    path('', include(router.urls)),
    path('currencies/', api_views.CurrencyListView.as_view(), name='currency_list'),
    path('auto-number/<str:doc_type>/', api_views.AutoNumberView.as_view(), name='auto_number'),
    path('num2words/', api_views.Num2WordsAPIView.as_view(), name='num2words'),
]
