from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomTagViewSet, RoomViewSet, BookingViewSet

router = DefaultRouter()
router.register("room-tags", RoomTagViewSet, basename="room-tags")
router.register("rooms", RoomViewSet, basename="rooms")
router.register("bookings", BookingViewSet, basename="bookings")

urlpatterns = [
    path("", include(router.urls)),
]
