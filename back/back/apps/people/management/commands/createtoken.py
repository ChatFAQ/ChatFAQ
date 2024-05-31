from django.core.management.base import BaseCommand, CommandError
from django.core import exceptions
from back.apps.people.models import User
from knox.models import AuthToken


class Command(BaseCommand):
    help = 'Creates a auth token given a user name'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Username of the user to create the token for')

    def handle(self, *args, **options):
        email = options['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f'User with email "{email}" does not exist')

        # check if the user belong to the RPC group:
        if not user.groups.filter(name="RPC").exists():
            raise CommandError(
                f'User with email "{email}" does not belong to the RPC group'
            )

        instance, token = AuthToken.objects.create(user=user)

        self.stdout.write(self.style.SUCCESS(f'Token for user "{email}" created: {token}'))
