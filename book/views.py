from datetime import datetime
from drf_yasg import openapi
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view
from book.serializers import (
    RoomSerializer,
    UserSerializer,
    BookingSerializer,
    RoomBookSerializer,
)
from book.models import Room, Booking
from book.services import available_choice, room_status, HOURS_ADD


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
@api_view(("POST", "GET", "DELETE"))
def booking_room(request):
    """Booking room"""
    if request.method == "POST":
        data = request.data
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
                }
            )
        if date_in > date_out:
            return Response(
                {
                    "data_out": "End of reservation time is less than the start of the reservation"
                }
            )

        rooms = Room.objects.filter(capacity=data["capacity"])
        free_rooms = []
        for room in rooms:
            if available_choice(room.id, date_in, date_out):
                free_rooms.append(room)
        if free_rooms:
            avail_room = free_rooms[0]
            try:
                user = User.objects.get(username=data["user"])
            except User.DoesNotExist:
                return Response({"error_message": "User does not exist"})
            booking = Booking.objects.create(
                room=avail_room, date_in=date_in, date_out=date_out, user=user
            )
            booker = Booking.objects.filter(pk=booking.pk)
            serializer = BookingSerializer(booker, many=True)
            booking.save()
            return JsonResponse(serializer.data, safe=False)

        else:
            return Response({"error_message": "No available rooms"})

    if request.method == "GET":
        booking = Booking.objects.all()
        booking = list(booking)
        serializer = BookingSerializer(booking, many=True)
        return JsonResponse(serializer.data, safe=False, status=201)

    if request.method == "DELETE":
        data = request.data
        booking = Booking.objects.filter(pk=data["pk"])
        booking.save()
        booking = list(booking)
        serializer = BookingSerializer(booking, many=True)
        return JsonResponse(serializer.data, safe=False, status=201)


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
