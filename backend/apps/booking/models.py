from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.postgres.fields import DateTimeRangeField
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.db.models import Q, F

from apps.centers.models import YouthCenter

# УБИРАЕМ ИМПОРТ ЗАДАЧ ОТСЮДА
# from apps.notifications.tasks import notify_user_of_approved_booking, notify_user_of_rejected_booking


class RoomTag(models.Model):
    # ... без изменений ...
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Тег помещения"
        verbose_name_plural = "Теги помещений"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Room(models.Model):
    # ... без изменений ...
    center = models.ForeignKey(YouthCenter, on_delete=models.CASCADE,
                               related_name="rooms")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="rooms/images/", blank=True, null=True)
    capacity = models.PositiveIntegerField(
        default=0)
    tags = models.ManyToManyField(RoomTag, related_name="rooms", blank=True)
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.SET_NULL, null=True,
                                    blank=True,
                                    related_name="responsible_rooms")
    responsible_phone = models.CharField(max_length=50,
                                         blank=True)

    class Meta:
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"
        ordering = ["center__name", "name"]
        unique_together = [("center", "name")]

    def __str__(self):
        return f"{self.center.name} — {self.name}"


class Status(models.TextChoices):
    # ... без изменений ...
    PENDING = "PENDING", "В ожидании"
    APPROVED = "APPROVED", "Одобрено"
    REJECTED = "REJECTED", "Отклонено"
    CANCELED = "CANCELED", "Отменено"


class Booking(models.Model):
    # ... (поля модели и Meta класс без изменений) ...
    room = models.ForeignKey(Room, on_delete=models.CASCADE,
                             related_name="bookings")
    time_slot = DateTimeRangeField()
    status = models.CharField(max_length=10, choices=Status.choices,
                              default=Status.PENDING)

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="bookings"
    )
    applicant_telegram_id = models.BigIntegerField(null=True, blank=True,
                                                   db_index=True)

    applicant_name = models.CharField(max_length=255)
    applicant_phone = models.CharField(max_length=50, blank=True)
    applicant_telegram_username = models.CharField(max_length=255, blank=True)

    comment = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-created_at"]
        constraints = [
            ExclusionConstraint(
                name="booking_no_overlap_if_approved",
                expressions=[
                    (F('room'), RangeOperators.EQUAL),
                    ('time_slot', RangeOperators.OVERLAPS),
                ],
                condition=Q(status="APPROVED"),
                index_type='GIST',
            ),
        ]

    def __str__(self):
        return f"{self.room} | {self.status} | {self.start_at} - {self.end_at}"

    @property
    def start_at(self):
        return self.time_slot.lower

    @property
    def end_at(self):
        return self.time_slot.upper

    def clean(self):
        if self.time_slot is None or self.start_at is None or self.end_at is None:
            raise ValidationError("Укажите корректный интервал времени.")
        if self.end_at <= self.start_at:
            raise ValidationError("Время окончания должно быть позже времени начала.")

    def approve(self):
        """Одобрение брони."""
        # ИМПОРТИРУЕМ ЗАДАЧУ ПРЯМО В МЕТОДЕ
        from apps.notifications.tasks import notify_user_of_approved_booking

        if Booking.objects.filter(
                room=self.room,
                status=Status.APPROVED,
                time_slot__overlap=(self.start_at, self.end_at)
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                "Невозможно одобрить: пересечение с другой одобренной бронью.")

        self.status = Status.APPROVED
        self.full_clean()
        self.save(update_fields=["status", "updated_at"])

        if self.applicant_telegram_id:
            notify_user_of_approved_booking.delay(self.id)

    def reject(self, reason: str):
        """Отклонение брони."""
        # ИМПОРТИРУЕМ ЗАДАЧУ ПРЯМО В МЕТОДЕ
        from apps.notifications.tasks import notify_user_of_rejected_booking

        if not reason:
            raise ValidationError("Укажите причину отклонения.")
        self.status = Status.REJECTED
        self.rejection_reason = reason
        self.save(update_fields=["status", "rejection_reason", "updated_at"])

        if self.applicant_telegram_id:
            notify_user_of_rejected_booking.delay(self.id)