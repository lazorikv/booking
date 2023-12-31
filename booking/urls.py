from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from booking.yasg import urlpatterns as doc_url
from book.views import *


router = DefaultRouter()
router.register(r'user', UserList, basename='User')
router.register(r'room', RoomList, basename='Room')

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    path('booking_room/', booking_room, name='bok'),
    path('free_rooms/', free_rooms, name='free'),
    path('occupied_rooms/', occupied_rooms, name='occupied'),
    path('bookings/', booked_rooms, name='bookings'),

]
urlpatterns += doc_url
