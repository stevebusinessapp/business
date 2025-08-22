from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Test email configuration and send test email'
    
    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address to send test email to')
        parser.add_argument('--check-only', action='store_true', help='Only check configuration, don\'t send email')
    
    def handle(self, *args, **options):
        self.stdout.write("=== Email Configuration Check ===")
        
        # Check configuration
        self.stdout.write(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            self.stdout.write(
                self.style.WARNING("\nUsing console backend - emails will only be printed to console")
            )
            self.stdout.write("Configure your email settings in .env file to send real emails")
            return
        
        if settings.EMAIL_HOST_USER == 'your-email@gmail.com' or not settings.EMAIL_HOST_USER:
            self.stdout.write(
                self.style.ERROR("\nEmail not configured! Please update your .env file:")
            )
            self.stdout.write("1. Set EMAIL_HOST_USER to your actual email")
            self.stdout.write("2. Set EMAIL_HOST_PASSWORD to your app password")
            self.stdout.write("3. Set DEFAULT_FROM_EMAIL to your actual email")
            return
        
        self.stdout.write(
            self.style.SUCCESS("\nEmail configuration looks good!")
        )
        
        if options['check_only']:
            return
        
        # Send test email
        email = options.get('email')
        if not email:
            self.stdout.write(self.style.ERROR("Please provide --email argument"))
            return
        
        try:
            send_mail(
                subject='Test Email from Django App',
                message='This is a test email to verify your email configuration is working correctly.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Test email sent successfully to {email}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to send email: {str(e)}")
            )
