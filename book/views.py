from datetime import datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from book.serializers import *
from book.models import *
from book.services import available_choice, room_status, HOURS_ADD


class RoomList(ModelViewSet):

    serializer_class = RoomSerializer
    queryset = Room.objects.all()


class UserList(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


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
        if date_in > date_out or date_in == date_out:
            return Response(
                {
                    "data_out": "End of reservation time is less/equal than the start of the reservation"
                },
                status=400,
            )
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response({"error_message": "User does not exist"}, status=400)
        if user.access == LIMITED_ACCESS:
            rooms = Room.objects.filter(capacity=data["capacity"]).filter(accessibility=FULL_ACCESS)
        else:
            rooms = Room.objects.filter(capacity=data["capacity"])
        free_room = ""
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
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response({"error_message": "User does not exist"}, status=400)
        if user.access == FULL_ACCESS:
            booking = Booking.objects.all()
        else:
            room = Room.objects.filter(accessibility=FULL_ACCESS)
            booking = Booking.objects.filter(room__in=room)
        if booking:
            booking = list(booking)
            serializer = BookingSerializer(booking, many=True)
            return JsonResponse(serializer.data, safe=False, status=200)
        return Response({"error_message": "No rooms booked"})

    if request.method == "DELETE":
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response({"error_message": "User does not exist"}, status=400)
        if user.role == User.MANAGER:
            Booking.objects.filter(pk=data["id"]).delete()
        else:
            try:
                booking = Booking.objects.get(pk=data["id"])
            except Booking.DoesNotExist:
                return Response({"error_message": "Booking does not exist"}, 400)
            if str(booking.user) == user.username:
                Booking.objects.filter(pk=data["id"]).delete()
            else:
                return Response({"error_message": "Permission denied"}, 400)
        return Response({"message": "Booking is deleted"}, 204)


@api_view(("GET",))
def free_rooms(request):
    """Free rooms"""
    if request.method == "GET":
        list_of_rooms = []
        user = User.objects.get(username=request.user)
        if user.access == FULL_ACCESS:
            rooms = Room.objects.all()
        else:
            rooms = Room.objects.filter(accessibility=FULL_ACCESS)
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
        user = User.objects.get(username=request.user)
        if user.access == FULL_ACCESS:
            rooms = Room.objects.all()
        else:
            rooms = Room.objects.filter(accessibility=FULL_ACCESS)
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
        user = User.objects.get(username=request.user)
        if user.access == FULL_ACCESS:
            rooms = Room.objects.all()
        else:
            rooms = Room.objects.filter(accessibility=FULL_ACCESS)
        booked_rooms = Booking.objects.filter(date_in__gt=time_now).filter(
            room__in=rooms
        )
        booking = list(booked_rooms)
        if booking:
            serializer = BookingSerializer(booking, many=True)
            return JsonResponse(serializer.data, safe=False, status=200)
        return Response({"message": "No booking for the future"}, 200)
