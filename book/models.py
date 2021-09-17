from django.db import models
from django.contrib.auth.models import User as OldUser
from django.contrib.auth import get_user_model as user_model
from book.management.managers import CustomUserManager


USER_MOD = user_model()
SML = "Small"
BIG = "Big"
CWR = "Employee"
MNG = "Manager"

ROOM_TYPES = [
    (SML, "Small"),
    (BIG, "Big")
]

WORK_TYPES = [
    (CWR, "Employee"),
    (MNG, "Manager")
]

FULL_ACCESS = (MNG, )
LIMITED_ACCESS = (CWR, )


class User(OldUser):

    role = models.CharField(max_length=20, choices=WORK_TYPES, default="Employee")

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username


class Room(models.Model):

    number = models.IntegerField(null=False, unique=True)
    capacity = models.IntegerField()
    type = models.CharField(max_length=20, choices=ROOM_TYPES, default="Small")

    def __str__(self):
        return str(self.number)


class Booking(models.Model):

    date_in = models.DateTimeField()
    date_out = models.DateTimeField()
    user = models.ForeignKey(
        USER_MOD, verbose_name="custom_user", on_delete=models.CASCADE, null=True
    )
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, verbose_name="room", null=True
    )
