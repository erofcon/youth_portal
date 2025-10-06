from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Room, RoomTag, Booking, Status
from .serializers import RoomSerializer, RoomTagSerializer, BookingSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


class RoomTagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = RoomTag.objects.all()
    serializer_class = RoomTagSerializer


class RoomViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = Room.objects.select_related("center").prefetch_related("tags")
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["center", "tags", "capacity"]

    @action(detail=True, methods=["get"], url_path="availability")
    def availability(self, request, pk=None):
        """
        Возвращает занятые интервалы по дате (только APPROVED).
        GET /rooms/{id}/availability/?date=YYYY-MM-DD
        """
        room = self.get_object()
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"detail": "Укажите параметр date=YYYY-MM-DD"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "Неверный формат даты"},
                            status=status.HTTP_400_BAD_REQUEST)

        start_dt = make_aware(datetime.combine(date, datetime.min.time()))
        end_dt = start_dt + timedelta(days=1)

        # Фильтруем интервалы, которые пересекаются с [start_dt, end_dt)
        qs = Booking.objects.filter(
            room=room,
            status=Status.APPROVED,
            time_slot__overlap=(start_dt, end_dt)
        )
        busy = [{"start": b.start_at, "end": b.end_at} for b in qs]

        return Response({"date": date, "busy_slots": busy})


class BookingViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Booking.objects.select_related("room", "room__center")
    serializer_class = BookingSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        """
        Если пользователь stateless (есть telegram_id) — ищем по applicant_telegram_id.
        Если пользователь реальный Django user — ищем по applicant.
        """
        u = request.user
        filters = Q()
        if getattr(u, 'is_authenticated', False):
            if hasattr(u, 'telegram_id'):
                filters |= Q(applicant_telegram_id=u.telegram_id)
            if getattr(u, 'pk', None):
                filters |= Q(applicant=u)
        if not filters:
            return Response([], status=200)

        user_bookings = Booking.objects.filter(filters).order_by('-created_at')

        page = self.paginate_queryset(user_bookings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(user_bookings, many=True)
        return Response(serializer.data)
