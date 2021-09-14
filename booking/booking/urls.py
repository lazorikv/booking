from django.contrib import admin
from django.urls import path
from booking.yasg import urlpatterns as doc_url
from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include
from book.views import RoomList, UserList, BookingList, booking_room


router = DefaultRouter()
router.register(r'user', UserList, basename='User')
router.register(r'booking', BookingList, basename='Booking')
router.register(r'room', RoomList, basename='Room')

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    path('booking_room/', booking_room, name='bok')
]
urlpatterns += doc_url
