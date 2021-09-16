from datetime import datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.utils import timezone
from book.models import User
from book.serializers import (
    RoomSerializer,
    UserSerializer,
    BookingSerializer,
    RoomBookSerializer,
)
from book.models import Room, Booking
from book.services import available_choice, room_status, HOURS_ADD


user_roles = {"Manager": ["Big", ],
              "Employee": ["Small", ]
              }


class RoomList(ModelViewSet):

    serializer_class = RoomSerializer
    queryset = Room.objects.all()


class UserList(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'capacity': openapi.Schema(type=openapi.TYPE_INTEGER, description='integer'),
        'date_in': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        'date_out': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        'user': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    }
))
@swagger_auto_schema(method='delete', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='integer'),
        'user': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    }
))


@api_view(("POST", "GET", "DELETE"))
def booking_room(request):
    """Booking room"""
    data = request.data
    if request.method == "POST":
        date_in = datetime.strptime(data["date_in"], "%Y-%m-%d %H:%M").replace(
            tzinfo=None
        )
        date_out = datetime.strptime(data["date_out"], "%Y-%m-%d %H:%M").replace(
            tzinfo=None
        )

        if date_in < timezone.now().replace(tzinfo=None)+HOURS_ADD:
            return Response(
                {
                    "data_in": "Еhe start time of the room reservation is less than the current time, "
                    "change the time of the reservation"
                },
                status=400
            )
        if date_in > date_out:
            return Response(
                {
                    "data_out": "End of reservation time is less than the start of the reservation"
                },
                status=400
            )
        try:
            user = User.objects.get(username=data["user"])
        except User.DoesNotExist:
            return Response({"error_message": "User does not exist"}, status=400)
        if user.role == 'Manager':
            rooms = Room.objects.filter(capacity=data["capacity"])
        else:
            rooms = Room.objects.filter(capacity=data["capacity"]).filter(type='Small')
        free_room = ''
        for room in rooms:
            if available_choice(room.id, date_in, date_out):
                free_room = room
                break
        if free_room:

            booking = Booking.objects.create(
                room=free_room, date_in=date_in, date_out=date_out, user=user
            )
            booker = Booking.objects.filter(pk=booking.pk)
            serializer = BookingSerializer(booker, many=True)
            booking.save()
            return JsonResponse(serializer.data, safe=False, status=201)

        else:
            return Response({"error_message": "No available rooms"})

    if request.method == "GET":
        user = User.objects.get(username="User-1")
        user_permissions = user_roles[user.role]
        rooms = Room.objects.filter(type__in=user_permissions)
        booking = Booking.objects.filter(room__in=rooms)
        booking = list(booking)
        serializer = BookingSerializer(booking, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)

    if request.method == "DELETE":
        user = User.objects.get(username=request.data['user'])
        if user.role == 'Manager':
            Booking.objects.filter(pk=data['id']).delete()
        else:
            try:
                booking = Booking.objects.get(pk=data['id'])
            except Booking.DoesNotExist:
                return Response({"error_message": "Booking does not exist"}, 400)
            if str(booking.user) == user.username:
                Booking.objects.filter(pk=data['id']).delete()
            else:
                return Response({"error_message": "Permission denied"}, 400)
        return Response({"error_message": "Booking is deleted"}, 204)


@api_view(("GET",))
def free_rooms(request):
    """Free rooms"""
    if request.method == "GET":
        list_of_rooms = []
        rooms = Room.objects.all()
        for room in rooms:
            if all(room_status(room)):
                list_of_rooms.append(room)
        booking = list_of_rooms
        serializer = RoomBookSerializer(booking, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)


@api_view(("GET",))
def occupied_rooms(request):
    """Occupied rooms"""
    if request.method == "GET":
        list_of_rooms = []
        rooms = Room.objects.all()
        for room in rooms:
            if all(room_status(room)) is False:
                list_of_rooms.append(room)
        booking = list_of_rooms
        serializer = RoomBookSerializer(booking, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)


@api_view(("GET",))
def booked_rooms(request):
    """All booking in future"""
    if request.method == "GET":
        time_now = timezone.now()
        booked_rooms = Booking.objects.filter(date_in__gt=time_now)
        booking = list(booked_rooms)
        serializer = BookingSerializer(booking, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
