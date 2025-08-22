from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import CompanyProfile, BankAccount
from .serializers import CompanyProfileSerializer, BankAccountSerializer
from .utils import get_available_currencies, generate_auto_number


class CompanyProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CompanyProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def upload_logo(self, request, pk=None):
        """Upload company logo"""
        company_profile = self.get_object()
        logo_file = request.FILES.get('logo')
        
        if not logo_file:
            return Response({'error': 'No logo file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete old logo if exists
        company_profile.delete_old_logo()
        
        company_profile.logo = logo_file
        company_profile.save()
        
        serializer = self.get_serializer(company_profile)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def upload_signature(self, request, pk=None):
        """Upload company signature"""
        company_profile = self.get_object()
        signature_file = request.FILES.get('signature')
        
        if not signature_file:
            return Response({'error': 'No signature file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete old signature if exists
        company_profile.delete_old_signature()
        
        company_profile.signature = signature_file
        company_profile.save()
        
        serializer = self.get_serializer(company_profile)
        return Response(serializer.data)


class BankAccountViewSet(viewsets.ModelViewSet):
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(company__user=self.request.user)

    def perform_create(self, serializer):
        company_profile = get_object_or_404(CompanyProfile, user=self.request.user)
        serializer.save(company=company_profile)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this bank account as default"""
        bank_account = self.get_object()
        
        # Update all accounts to not default, then set this one as default
        BankAccount.objects.filter(company=bank_account.company).update(is_default=False)
        bank_account.is_default = True
        bank_account.save()
        
        serializer = self.get_serializer(bank_account)
        return Response(serializer.data)


class CurrencyListView(APIView):
    """Get list of available currencies"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        currencies = get_available_currencies()
        return Response(currencies)


class AutoNumberView(APIView):
    """Generate auto number for documents"""
    permission_classes = [IsAuthenticated]

    def get(self, request, doc_type):
        try:
            company_profile = request.user.company_profile
            auto_number = generate_auto_number(doc_type, company_profile)
            return Response({'auto_number': auto_number})
        except CompanyProfile.DoesNotExist:
            return Response({'error': 'Company profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class Num2WordsAPIView(APIView):
    """Convert a number to words for receipts and invoices."""
    permission_classes = [AllowAny]

    def get(self, request):
        from decimal import Decimal, InvalidOperation
        try:
            amount = request.GET.get('amount')
            currency = request.GET.get('currency', 'NGN')
            if amount is None:
                return Response({'error': 'Missing amount parameter'}, status=400)
            try:
                amount_decimal = Decimal(amount)
            except InvalidOperation:
                return Response({'error': 'Invalid amount'}, status=400)
            try:
                from num2words import num2words
                words = num2words(amount_decimal, lang='en')
                words = f"{words} {currency.lower()} only"
            except Exception:
                words = str(amount_decimal)
            return Response({'words': words})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
