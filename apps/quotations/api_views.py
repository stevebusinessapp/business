from rest_framework import viewsets, permissions
from .models import Quotation, QuotationItem, QuotationTemplate
from .serializers import QuotationSerializer, QuotationItemSerializer, QuotationTemplateSerializer

class QuotationViewSet(viewsets.ModelViewSet):
    serializer_class = QuotationSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        company = self.request.user.companyprofile_set.first()
        return Quotation.objects.filter(company=company)

class QuotationItemViewSet(viewsets.ModelViewSet):
    serializer_class = QuotationItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        company = self.request.user.companyprofile_set.first()
        return QuotationItem.objects.filter(quotation__company=company)

class QuotationTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = QuotationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        company = self.request.user.companyprofile_set.first()
        return QuotationTemplate.objects.filter(company=company) 