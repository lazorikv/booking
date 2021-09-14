from factory.django import DjangoModelFactory
from factory.faker import Faker
from factory import Sequence, PostGenerationMethodCall, sequence, LazyAttribute
from django.contrib.auth.models import User
from book.models import Room, Booking
from datetime import timedelta


class UserFactory(DjangoModelFactory):

    first_name = Faker('first_name')
    last_name = Faker('last_name')
    email = Faker('email')
    username = Sequence(lambda n: f'User-{n}')

    class Meta:
        model = User
        django_get_or_create = ['username']


class RoomFactory(DjangoModelFactory):

    number = Sequence(lambda n: n)
    capacity = Faker('pyint', min_value=2, max_value=5)

    class Meta:
        model = Room
        django_get_or_create = ['number']


