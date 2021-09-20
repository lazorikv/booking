from django.contrib import admin
from book.models import Room, Booking
from book.models import User


class RoomAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["capacity", "number", "accessibility", "type"]}),
    ]

    list_display = ("id", "number", "capacity", "accessibility", "type")
    search_fields = ["number"]


class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["username", "first_name", "last_name", 'password', "email", "role", "access"]}),
    ]

    list_display = ("pk", "username", "first_name", "last_name", 'access', "email", "role")
    search_fields = ["username"]


class BookingAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["date_in", "date_out", "user", "room"]}),
    ]

    list_display = ("date_in", "date_out", "user", "room")
    search_fields = ["room"]


admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(User, UserAdmin)
