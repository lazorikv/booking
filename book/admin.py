from django.contrib import admin
from book.models import Room, Booking
from book.models import CustomUser


class RoomAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["capacity", "number"]}),
    ]

    list_display = ("number", "capacity")
    search_fields = ["number"]


class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["id", "username", "first_name", "last_name", "email", "role"]}),
    ]

    list_display = ("id", "username", "first_name", "last_name", "email", "role")
    search_fields = ["username"]


class BookingAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["date_in", "date_out", "user", "room"]}),
    ]

    list_display = ("date_in", "date_out", "user", "room")
    search_fields = ["room"]


admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(CustomUser, UserAdmin)
