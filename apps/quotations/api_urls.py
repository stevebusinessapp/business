from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'quotations', api_views.QuotationViewSet, basename='quotation')
router.register(r'quotation-items', api_views.QuotationItemViewSet, basename='quotationitem')
router.register(r'quotation-templates', api_views.QuotationTemplateViewSet, basename='quotationtemplate')

urlpatterns = [
    path('', include(router.urls)),
]
