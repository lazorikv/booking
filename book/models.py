from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


SML = "Small"
BIG = "Big"
CWR = "Employee"
MNG = "Manager"

ROOM_TYPES = (
    (SML, "Small"),
    (BIG, "Big")
)

WORK_TYPES = (
    (CWR, "Employee"),
    (MNG, "Manager")
)


class CustomUser(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    role = models.CharField(max_length=20, choices=WORK_TYPES, default="Employee")

    objects = CustomUserManager()

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
        CustomUser, verbose_name="customuser", on_delete=models.CASCADE, null=True
    )
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, verbose_name="room", null=True
    )
