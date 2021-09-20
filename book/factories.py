from factory.django import DjangoModelFactory
from factory.faker import Faker
import factory.fuzzy
from factory import Sequence
from book.models import *


ROOM_CHOICES = [x[0] for x in ROOM_TYPES]
ROLE_CHOICES = [x[0] for x in WORK_TYPES]
ACCESS_CHOICES = [x[0] for x in ACCESS_TYPES]


class UserFactory(DjangoModelFactory):

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    username = Sequence(lambda n: f"User-{n}")
    password = Sequence(lambda n: f"User-{n}")
    role = factory.fuzzy.FuzzyChoice(ROLE_CHOICES)
    access = factory.fuzzy.FuzzyChoice(ACCESS_CHOICES)

    class Meta:
        model = User
        django_get_or_create = ["username"]

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class RoomFactory(DjangoModelFactory):

    number = Sequence(lambda n: n)
    capacity = Faker("pyint", min_value=2, max_value=5)
    accessibility = factory.fuzzy.FuzzyChoice(ACCESS_CHOICES)
    type = factory.fuzzy.FuzzyChoice(ROOM_CHOICES)

    class Meta:
        model = Room
        django_get_or_create = ["number"]
