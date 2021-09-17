from datetime import datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.utils import timezone
from book.serializers import (
    RoomSerializer,
    UserSerializer,
    BookingSerializer,
    RoomBookSerializer,
)
from book import models
from book.services import available_choice, room_status, HOURS_ADD


user_roles = {
    models.MNG: [models.BIG, models.SML],
    models.CWR: [
        models.SML,
    ],
}


class RoomList(ModelViewSet):

    serializer_class = RoomSerializer
    queryset = models.Room.objects.all()


class UserList(ModelViewSet):
    serializer_class = UserSerializer
    queryset = models.User.objects.all()


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "capacity": openapi.Schema(
                type=openapi.TYPE_INTEGER, description="integer"
            ),
            "date_in": openapi.Schema(type=openapi.TYPE_STRING, description="string"),
            "date_out": openapi.Schema(type=openapi.TYPE_STRING, description="string"),
            "user": openapi.Schema(type=openapi.TYPE_STRING, description="string"),
        },
    ),
)
@swagger_auto_schema(
    method="delete",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="integer"),
            "user": openapi.Schema(type=openapi.TYPE_STRING, description="string"),
        },
    ),
)
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

        if date_in < timezone.now().replace(tzinfo=None) + HOURS_ADD:
            return Response(
                {
                    "data_in": "Еhe start time of the room reservation is less than the current time, "
                    "change the time of the reservation"
                },
                status=400,
            )
        if date_in > date_out:
            return Response(
                {
                    "data_out": "End of reservation time is less than the start of the reservation"
                },
                status=400,
            )
        try:
            user = models.User.objects.get(username=data["user"])
        except models.User.DoesNotExist:
            return Response({"error_message": "User does not exist"}, status=400)
        rooms = []
        if user.role in models.FULL_ACCESS:
            rooms = models.Room.objects.filter(capacity=data["capacity"])
        elif user.role in models.LIMITED_ACCESS:
            rooms = models.Room.objects.filter(capacity=data["capacity"]).filter(type="Small")
        free_room = ""
        for room in rooms:
            if available_choice(room.id, date_in, date_out):
                free_room = room
                break
        if free_room:

            booking = models.Booking.objects.create(
                room=free_room, date_in=date_in, date_out=date_out, user=user
            )
            booker = models.Booking.objects.filter(pk=booking.pk)
            serializer = BookingSerializer(booker, many=True)
            booking.save()
            return JsonResponse(serializer.data, safe=False, status=201)

        else:
            return Response({"error_message": "No available rooms"})

    if request.method == "GET":
        try:
            user = models.User.objects.get(username=request.user)
        except models.User.DoesNotExist:
            return Response({"error_message": "User does not exist"}, status=400)
        user_permissions = user_roles[user.role]
        rooms = models.Room.objects.filter(type__in=user_permissions)
        booking = models.Booking.objects.filter(room__in=rooms)
        if booking:
            booking = list(booking)
            serializer = BookingSerializer(booking, many=True)
            return JsonResponse(serializer.data, safe=False, status=200)
        return Response({"error_message": "No rooms booked"})

    if request.method == "DELETE":
        try:
            user = models.User.objects.get(username=request.user)
        except models.User.DoesNotExist:
            return Response({"error_message": "User does not exist"}, status=400)
        if user.role in models.FULL_ACCESS:
            models.Booking.objects.filter(pk=data["id"]).delete()
        else:
            try:
                booking = models.Booking.objects.get(pk=data["id"])
            except models.Booking.DoesNotExist:
                return Response({"error_message": "Booking does not exist"}, 400)
            if str(booking.user) == user.username:
                models.Booking.objects.filter(pk=data["id"]).delete()
            else:
                return Response({"error_message": "Permission denied"}, 400)
        return Response({"message": "Booking is deleted"}, 204)


@api_view(("GET",))
def free_rooms(request):
    """Free rooms"""
    if request.method == "GET":
        print("olsmdkfo;lsnad", request.user)
        print("osdfsadf", request.data)
        list_of_rooms = []
        user = models.User.objects.get(username=request.user)
        user_permissions = user_roles[user.role]
        rooms = models.Room.objects.filter(type__in=user_permissions)
        for room in rooms:
            if all(room_status(room)):
                list_of_rooms.append(room)
        booking = list_of_rooms
        if booking:
            serializer = RoomBookSerializer(booking, many=True)
            return JsonResponse(serializer.data, safe=False, status=200)
        return Response({"message": "All rooms is occupied now"}, 200)


@api_view(("GET",))
def occupied_rooms(request):
    """Occupied rooms"""
    if request.method == "GET":
        list_of_rooms = []
        user = models.User.objects.get(username=request.user)
        user_permissions = user_roles[user.role]
        rooms = models.Room.objects.filter(type__in=user_permissions)
        for room in rooms:
            if all(room_status(room)) is False:
                list_of_rooms.append(room)
        booking = list_of_rooms
        if booking:
            serializer = RoomBookSerializer(booking, many=True)
            return JsonResponse(serializer.data, safe=False, status=200)
        return Response({"message": "All rooms is free now"}, 200)


@api_view(("GET",))
def booked_rooms(request):
    """All booking in future"""
    if request.method == "GET":
        time_now = timezone.now()
        user = models.User.objects.get(username=request.user)
        user_permissions = user_roles[user.role]
        rooms = models.Room.objects.filter(type__in=user_permissions)
        booked_rooms = models.Booking.objects.filter(date_in__gt=time_now).filter(
            room__in=rooms
        )
        booking = list(booked_rooms)
        if booking:
            serializer = BookingSerializer(booking, many=True)
            return JsonResponse(serializer.data, safe=False, status=200)
        return Response({"message": "No booking for the future"}, 200)
