from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet
from book.serializers import RoomSerializer, UserSerializer, BookingSerializer
from book.models import Room, Booking
from book.services import available_choice
from rest_framework.response import Response
from datetime import datetime
from rest_framework.decorators import api_view
from django.http import JsonResponse


class RoomList(ModelViewSet):

    serializer_class = RoomSerializer
    queryset = Room.objects.all()


class UserList(ModelViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()


class BookingList(ModelViewSet):

    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.order_by('date_in')


@api_view(('POST', 'GET'))
def booking_room(request):
    if request.method == 'POST':
        data = request.data
        date_in = datetime.strptime(data['date_in'], '%Y-%m-%d %H:%M').replace(tzinfo=None)
        date_out = datetime.strptime(data['date_out'], '%Y-%m-%d %H:%M').replace(tzinfo=None)
        rooms = Room.objects.filter(capacity=data['capacity'])
        free_rooms = []
        for room in rooms:
            if available_choice(room.id, date_in, date_out):
                free_rooms.append(room)
        if free_rooms:
            avail_room = free_rooms[0]
            user = User.objects.get(username=data['user'])
            booking = Booking.objects.create(room=avail_room, date_in=date_in,
                                             date_out=date_out, user=user)
            booker = Booking.objects.filter(pk=booking.pk)
            serializer = BookingSerializer(booker, many=True)
            booking.save()
            return JsonResponse(serializer.data, safe=False)
        else:
            return Response("No available rooms")

    if request.method == 'GET':

        booking = Booking.objects.all()
        booking = list(booking)
        serializer = BookingSerializer(booking, many=True)
        return JsonResponse(serializer.data, safe=False, status=201)
