from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
import json

from .models import CompanyProfile, BankAccount
from .forms import CompanyProfileForm, BankAccountForm
from .utils import generate_auto_number, get_currency_info, format_currency


class CompanyProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_company_profile_creation(self):
        """Test company profile creation"""
        company_profile = CompanyProfile.objects.create(
            user=self.user,
            company_name='Test Company',
            email='company@test.com',
            phone='+1234567890',
            address='123 Test Street',
            website='https://test.com'
        )
        
        self.assertEqual(company_profile.company_name, 'Test Company')
        self.assertEqual(company_profile.user, self.user)
        self.assertEqual(str(company_profile), 'Test Company')
        
    def test_company_profile_defaults(self):
        """Test company profile default values"""
        company_profile = CompanyProfile.objects.create(
            user=self.user,
            company_name='Test Company',
            email='company@test.com',
            phone='+1234567890',
            address='123 Test Street'
        )
        
        self.assertEqual(company_profile.default_tax, 0.00)
        self.assertEqual(company_profile.default_discount, 0.00)
        self.assertEqual(company_profile.default_shipping_fee, 0.00)
        self.assertEqual(company_profile.currency_code, 'USD')
        self.assertEqual(company_profile.currency_symbol, '$')
        self.assertEqual(company_profile.custom_charges, {})
        
    def test_company_profile_one_to_one_relationship(self):
        """Test that each user can have only one company profile"""
        CompanyProfile.objects.create(
            user=self.user,
            company_name='Test Company 1',
            email='company1@test.com',
            phone='+1234567890',
            address='123 Test Street'
        )
        
        # Trying to create another profile for the same user should work
        # but accessing via user.company_profile should return the first one
        with self.assertRaises(Exception):
            CompanyProfile.objects.create(
                user=self.user,
                company_name='Test Company 2',
                email='company2@test.com',
                phone='+1234567891',
                address='456 Test Avenue'
            )


class BankAccountModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.company_profile = CompanyProfile.objects.create(
            user=self.user,
            company_name='Test Company',
            email='company@test.com',
            phone='+1234567890',
            address='123 Test Street'
        )
        
    def test_bank_account_creation(self):
        """Test bank account creation"""
        bank_account = BankAccount.objects.create(
            company=self.company_profile,
            bank_name='Test Bank',
            account_name='Test Account',
            account_number='1234567890',
            is_default=True
        )
        
        self.assertEqual(bank_account.bank_name, 'Test Bank')
        self.assertEqual(bank_account.company, self.company_profile)
        self.assertTrue(bank_account.is_default)
        self.assertEqual(str(bank_account), 'Test Bank - 1234567890')
        
    def test_default_bank_account_logic(self):
        """Test that only one bank account can be default per company"""
        # Create first bank account as default
        bank_account1 = BankAccount.objects.create(
            company=self.company_profile,
            bank_name='Test Bank 1',
            account_name='Test Account 1',
            account_number='1234567890',
            is_default=True
        )
        
        # Create second bank account as default
        bank_account2 = BankAccount.objects.create(
            company=self.company_profile,
            bank_name='Test Bank 2',
            account_name='Test Account 2',
            account_number='0987654321',
            is_default=True
        )
        
        # Refresh from database
        bank_account1.refresh_from_db()
        bank_account2.refresh_from_db()
        
        # First account should no longer be default
        self.assertFalse(bank_account1.is_default)
        self.assertTrue(bank_account2.is_default)


class CompanyProfileFormTest(TestCase):
    def test_valid_form(self):
        """Test valid company profile form"""
        form_data = {
            'company_name': 'Test Company',
            'email': 'company@test.com',
            'phone': '+1234567890',
            'address': '123 Test Street',
            'website': 'https://test.com',
            'default_tax': 10.00,
            'default_discount': 5.00,
            'default_shipping_fee': 15.00,
            'currency_code': 'USD',
            'currency_symbol': '$',
            'custom_charges': '{"handling_fee": 10.00}'
        }
        
        form = CompanyProfileForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_invalid_email(self):
        """Test form with invalid email"""
        form_data = {
            'company_name': 'Test Company',
            'email': 'invalid-email',
            'phone': '+1234567890',
            'address': '123 Test Street'
        }
        
        form = CompanyProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
    def test_invalid_custom_charges_json(self):
        """Test form with invalid JSON in custom charges"""
        form_data = {
            'company_name': 'Test Company',
            'email': 'company@test.com',
            'phone': '+1234567890',
            'address': '123 Test Street',
            'custom_charges': 'invalid json'
        }
        
        form = CompanyProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('custom_charges', form.errors)


class BankAccountFormTest(TestCase):
    def test_valid_form(self):
        """Test valid bank account form"""
        form_data = {
            'bank_name': 'Test Bank',
            'account_name': 'Test Account',
            'account_number': '1234567890',
            'is_default': True
        }
        
        form = BankAccountForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_short_account_number(self):
        """Test form with short account number"""
        form_data = {
            'bank_name': 'Test Bank',
            'account_name': 'Test Account',
            'account_number': '123',
            'is_default': False
        }
        
        form = BankAccountForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('account_number', form.errors)


class UtilsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.company_profile = CompanyProfile.objects.create(
            user=self.user,
            company_name='Test Company',
            email='company@test.com',
            phone='+1234567890',
            address='123 Test Street'
        )
        
    def test_get_currency_info(self):
        """Test currency info retrieval"""
        usd_info = get_currency_info('USD')
        self.assertEqual(usd_info['symbol'], '$')
        self.assertEqual(usd_info['name'], 'US Dollar')
        
        eur_info = get_currency_info('EUR')
        self.assertEqual(eur_info['symbol'], '€')
        self.assertEqual(eur_info['name'], 'Euro')
        
        invalid_info = get_currency_info('INVALID')
        self.assertIsNone(invalid_info)
        
    def test_format_currency(self):
        """Test currency formatting"""
        formatted = format_currency(1234.56, '$', 2)
        self.assertEqual(formatted, '$1,234.56')
        
        formatted_eur = format_currency(1000, '€', 2)
        self.assertEqual(formatted_eur, '€1,000.00')
        
    def test_generate_auto_number(self):
        """Test auto number generation"""
        auto_number = generate_auto_number('invoice', self.company_profile)
        self.assertIn('INV-', auto_number)
        self.assertTrue(auto_number.endswith('-0001'))
        
        quotation_number = generate_auto_number('quotation', self.company_profile)
        self.assertIn('QUO-', quotation_number)


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.company_profile = CompanyProfile.objects.create(
            user=self.user,
            company_name='Test Company',
            email='company@test.com',
            phone='+1234567890',
            address='123 Test Street'
        )
        
    def test_dashboard_view_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_dashboard_view_with_company_profile(self):
        """Test dashboard view with existing company profile"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Company')
        
    def test_company_profile_view_get(self):
        """Test company profile view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:company_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Company')
        
    def test_company_profile_view_post(self):
        """Test company profile view POST request"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'company_name': 'Updated Company',
            'email': 'updated@test.com',
            'phone': '+1234567890',
            'address': '123 Updated Street',
            'website': 'https://updated.com',
            'default_tax': 15.00,
            'default_discount': 10.00,
            'default_shipping_fee': 20.00,
            'currency_code': 'EUR',
            'currency_symbol': '€',
            'custom_charges': '{}'
        }
        
        response = self.client.post(reverse('core:company_profile'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Check if profile was updated
        self.company_profile.refresh_from_db()
        self.assertEqual(self.company_profile.company_name, 'Updated Company')
        self.assertEqual(self.company_profile.currency_code, 'EUR')
        
    def test_bank_accounts_view(self):
        """Test bank accounts view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:bank_accounts'))
        self.assertEqual(response.status_code, 200)
        
    def test_add_bank_account(self):
        """Test adding bank account"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'bank_name': 'New Bank',
            'account_name': 'New Account',
            'account_number': '9876543210',
            'is_default': True
        }
        
        response = self.client.post(reverse('core:bank_accounts'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check if bank account was created
        bank_account = BankAccount.objects.get(account_number='9876543210')
        self.assertEqual(bank_account.bank_name, 'New Bank')
        self.assertTrue(bank_account.is_default)


class APITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.company_profile = CompanyProfile.objects.create(
            user=self.user,
            company_name='Test Company',
            email='company@test.com',
            phone='+1234567890',
            address='123 Test Street'
        )
        
    def test_update_currency_api(self):
        """Test currency update API"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {'currency_code': 'EUR'}
        response = self.client.post(
            reverse('core:update_currency'),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['currency_code'], 'EUR')
        
        # Check if profile was updated
        self.company_profile.refresh_from_db()
        self.assertEqual(self.company_profile.currency_code, 'EUR')
