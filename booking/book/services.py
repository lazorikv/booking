from book.models import Booking
from datetime import timedelta


HOURS_ADD = timedelta(hours=3)


def available_choice(room, date_in, date_out):

    avail_choice = []
    room_book = Booking.objects.filter(room=room)
    for room in room_book:
        if date_out < room.date_in.replace(tzinfo=None)+HOURS_ADD or \
                date_in > room.date_out.replace(tzinfo=None)+HOURS_ADD:
            avail_choice.append(True)
        else:
            avail_choice.append(False)

    return all(avail_choice)
