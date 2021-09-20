from django.core.management.base import BaseCommand
from book.factories import *


class Command(BaseCommand):

    help = "Generate data"

    def add_arguments(self, parser):
        parser.add_argument("--amount", type=int, help="The amount of fake data")

    def _generate_users(self, amount: int):
        for _ in range(amount):
            UserFactory()
            RoomFactory()

    def handle(self, *args, **options):
        amount = options.get("amount", 10)
        self._generate_users(amount)
