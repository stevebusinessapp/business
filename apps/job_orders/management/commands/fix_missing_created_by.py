from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.job_orders.models import JobOrder

class Command(BaseCommand):
    help = 'Fix JobOrder objects with missing created_by by setting it to a specified user.'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str, help='Username, email, or user ID to set as created_by')

    def handle(self, *args, **options):
        User = get_user_model()
        user_arg = options['user']
        user = None
        try:
            if user_arg.isdigit():
                user = User.objects.get(pk=int(user_arg))
            else:
                # Try username, then email
                try:
                    user = User.objects.get(username=user_arg)
                except Exception:
                    try:
                        user = User.objects.get(email=user_arg)
                    except Exception:
                        pass
            if not user:
                raise User.DoesNotExist
        except User.DoesNotExist:
            raise CommandError(f'User {user_arg} does not exist (tried username, email, and ID).')

        missing = JobOrder.objects.filter(created_by__isnull=True)
        count = missing.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No job orders with missing created_by.'))
            return
        missing.update(created_by=user)
        self.stdout.write(self.style.SUCCESS(f'Fixed {count} job orders with missing created_by.')) 