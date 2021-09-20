from factory.django import DjangoModelFactory
from factory.faker import Faker
import factory.fuzzy
from factory import Sequence, LazyFunction
from django.contrib.auth.hashers import make_password
from book.models import *


ROOM_CHOICES = [x[0] for x in ROOM_TYPES]
ROLE_CHOICES = [x[0] for x in WORK_TYPES]
ACCESS_CHOICES = [x[0] for x in ACCESS_TYPES]


class UserFactory(DjangoModelFactory):

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    username = Sequence(lambda n: f"User-{n}")
    password = LazyFunction(lambda: make_password('pi3.1415'))
    access = factory.fuzzy.FuzzyChoice(ACCESS_CHOICES)
    role = factory.fuzzy.FuzzyChoice(ROLE_CHOICES)

    class Meta:
        model = User
        django_get_or_create = ["username"]


class RoomFactory(DjangoModelFactory):

    number = Sequence(lambda n: n)
    capacity = Faker("pyint", min_value=2, max_value=5)
    accessibility = factory.fuzzy.FuzzyChoice(ACCESS_CHOICES)
    type = factory.fuzzy.FuzzyChoice(ROOM_CHOICES)

    class Meta:
        model = Room
        django_get_or_create = ["number"]
