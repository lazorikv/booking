from factory.django import DjangoModelFactory
from factory.faker import Faker
from factory import fuzzy
from factory import Sequence
from book.models import *


ACCESS_CHOICES = [FULL_ACCESS, LIMITED_ACCESS]


class UserFactory(DjangoModelFactory):

    ROLE_CHOICES = [User.EMPLOYEE, User.MANAGER]

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    username = Sequence(lambda n: f"User-{n}")
    password = Sequence(lambda n: f"User-{n}")
    role = fuzzy.FuzzyChoice(ROLE_CHOICES)
    access = fuzzy.FuzzyChoice(ACCESS_CHOICES)

    class Meta:
        model = User
        django_get_or_create = ["username"]

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class RoomFactory(DjangoModelFactory):

    ROOM_CHOICES = [Room.BIG_ROOM, Room.SMALL_ROOM]

    number = Sequence(lambda n: n)
    capacity = Faker("pyint", min_value=2, max_value=5)
    accessibility = fuzzy.FuzzyChoice(ACCESS_CHOICES)
    type = fuzzy.FuzzyChoice(ROOM_CHOICES)

    class Meta:
        model = Room
        django_get_or_create = ["number"]
