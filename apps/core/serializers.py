from rest_framework import serializers
from .models import CompanyProfile, BankAccount


class CompanyProfileSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    signature_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanyProfile
        fields = [
            'id', 'company_name', 'email', 'phone', 'address', 'website',
            'logo', 'logo_url', 'signature', 'signature_url',
            'default_tax', 'default_discount', 'default_shipping_fee',
            'custom_charges', 'currency_code', 'currency_symbol',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None

    def get_signature_url(self, obj):
        if obj.signature:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.signature.url)
            return obj.signature.url
        return None

    def validate_custom_charges(self, value):
        """Validate custom charges format"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Custom charges must be a dictionary")
        
        for key, charge_value in value.items():
            if not isinstance(charge_value, (int, float)):
                raise serializers.ValidationError(f"Charge value for '{key}' must be a number")
            if charge_value < 0:
                raise serializers.ValidationError(f"Charge value for '{key}' cannot be negative")
        
        return value


class BankAccountSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    
    class Meta:
        model = BankAccount
        fields = [
            'id', 'company', 'company_name', 'bank_name', 'account_name',
            'account_number', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['company', 'created_at', 'updated_at']

    def validate_account_number(self, value):
        """Validate account number format"""
        if not value.replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Account number can only contain digits, spaces, and hyphens")
        return value

    def create(self, validated_data):
        # Handle default bank account logic
        bank_account = BankAccount(**validated_data)
        if bank_account.is_default:
            BankAccount.objects.filter(company=bank_account.company).update(is_default=False)
        bank_account.save()
        return bank_account

    def update(self, instance, validated_data):
        # Handle default bank account logic
        if validated_data.get('is_default', False):
            BankAccount.objects.filter(company=instance.company).exclude(id=instance.id).update(is_default=False)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CompanyProfileCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for company profile creation"""
    
    class Meta:
        model = CompanyProfile
        fields = [
            'company_name', 'email', 'phone', 'address', 'website',
            'default_tax', 'default_discount', 'default_shipping_fee',
            'currency_code', 'currency_symbol'
        ]

    def validate_email(self, value):
        """Validate email format"""
        if not value:
            raise serializers.ValidationError("Email is required")
        return value

    def validate_company_name(self, value):
        """Validate company name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Company name must be at least 2 characters long")
        return value.strip()


class BankAccountCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for bank account creation"""
    
    class Meta:
        model = BankAccount
        fields = ['bank_name', 'account_name', 'account_number', 'is_default']

    def validate_bank_name(self, value):
        """Validate bank name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Bank name must be at least 2 characters long")
        return value.strip()

    def validate_account_name(self, value):
        """Validate account name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Account name must be at least 2 characters long")
        return value.strip()
