from django.contrib import admin
from django.contrib.auth.models import User
from book.models import Room, Booking


class RoomAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['capacity', 'number']}),
    ]

    list_display = ('number', "capacity")
    search_fields = ['number']


class BookingAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['date_in', 'date_out', 'user', 'room']}),
    ]

    list_display = ('date_in', 'date_out', 'user', 'room')
    search_fields = ['room']


admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
