from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.receipts.models import Receipt

class Command(BaseCommand):
    help = 'Set the created_by field of all receipts to the specified user (by username or email)'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str, help='Username or email of the user to assign to all receipts')

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
        count = Receipt.objects.exclude(created_by=user).count()
        Receipt.objects.all().update(created_by=user)
        self.stdout.write(self.style.SUCCESS(f'Updated {count} receipts to user {user.username}')) 