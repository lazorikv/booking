from datetime import timedelta
from django.utils import timezone
from book.models import Booking


HOURS_ADD = timedelta(hours=3)


def available_choice(room, date_in, date_out):
    room_info = []
    room_bookings = Booking.objects.filter(room=room)
    for booking in room_bookings:
        if (
            date_out < booking.date_in.replace(tzinfo=None) + HOURS_ADD
            or date_in > booking.date_out.replace(tzinfo=None) + HOURS_ADD
        ):
            room_info.append(True)
        else:
            room_info.append(False)

    return all(room_info)


def room_status(room):
    time_now = timezone.now()
    bookings = Booking.objects.filter(room=room)
    free_room = []
    for booking in bookings:
        if time_now < booking.date_in or time_now > booking.date_out:
            free_room.append(True)
        else:
            free_room.append(False)
    return free_room
