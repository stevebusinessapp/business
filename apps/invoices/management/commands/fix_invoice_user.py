from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.invoices.models import Invoice

class Command(BaseCommand):
    help = 'Set the user field of all invoices to the specified user (by username or email)'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str, help='Username or email of the user to assign to all invoices')

    def handle(self, *args, **options):
        User = get_user_model()
        user_arg = options['user']
        try:
            user = User.objects.get(username=user_arg)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=user_arg)
            except User.DoesNotExist:
                raise CommandError(f'User {user_arg} does not exist (tried username and email).')
        count = Invoice.objects.exclude(user=user).count()
        Invoice.objects.all().update(user=user)
        self.stdout.write(self.style.SUCCESS(f'Updated {count} invoices to user {user.username}')) 