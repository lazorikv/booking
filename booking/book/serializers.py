from django.contrib.auth.models import User
from book.models import Room, Booking
from rest_framework import serializers
from django.utils import timezone
from book.services import HOURS_ADD


class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking

        fields = [
            'pk', 'room', "date_in", 'date_out', 'user'
        ]

    def update(self, instance, validated_data):
        instance.date_in = validated_data.get('date_in', instance.date_in)
        instance.date_out = validated_data.get('date_out', instance.date_out)
        instance.user = validated_data.get('user', instance.user)
        instance.room = validated_data.get('room', instance.room)
        instance.save()
        return instance


class BookingDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking

        fields = [
            'pk', 'room', "date_in", 'date_out', 'user'
        ]

    def create(self, validated_data):
        return Booking.objects.create(**validated_data)


class RoomBookSerializer(serializers.ModelSerializer):

    booking_room = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'pk', 'number', 'capacity', 'booking_room',
        ]

    def get_booking_room(self, obj):
        ordered_queryset = Booking.objects.filter(date_in__gte=timezone.now().replace(tzinfo=None)+HOURS_ADD).filter(room=obj.id)
        return BookingSerializer(ordered_queryset, many=True).data


class RoomSerializer(serializers.ModelSerializer):

    booking_room = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'pk', 'number', 'capacity', 'booking_room',
        ]

    def create(self, validated_data):
        return Room.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    def get_booking_room(self, obj):
        ordered_queryset = Booking.objects.filter(room=obj.id).order_by('-date_in')
        return BookingSerializer(ordered_queryset, many=True).data


class UserSerializer(serializers.ModelSerializer):

    booking = BookingDetailSerializer(source='booking_set', many=True, read_only=True)

    class Meta:
        model = User

        fields = [
            'pk', 'username', 'first_name', 'last_name', 'email', 'booking'
        ]

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
