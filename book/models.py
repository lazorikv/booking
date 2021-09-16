from django.db import models
from django.contrib.auth.models import User


SML = "Small"
BIG = "Big"

ROOM_TYPES = (
    (SML, "Small"),
    (BIG, "Big")
)


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
        User, verbose_name="user", on_delete=models.CASCADE, null=True
    )
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, verbose_name="room", null=True
    )
