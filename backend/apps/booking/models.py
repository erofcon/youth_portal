from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.postgres.fields import DateTimeRangeField
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.db.models import Q, F

from apps.centers.models import YouthCenter


class RoomTag(models.Model):
    """
    Тег/особенность помещения (конференции, лекции, wi-fi и т.д.).
    """

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Тег помещения"
        verbose_name_plural = "Теги помещений"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Room(models.Model):
    """
    Помещение для бронирования.
    """
    center = models.ForeignKey(YouthCenter, on_delete=models.CASCADE,
                               related_name="rooms")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="rooms/images/", blank=True, null=True)
    capacity = models.PositiveIntegerField(
        default=0)  # вместимость, если известна
    tags = models.ManyToManyField(RoomTag, related_name="rooms", blank=True)

    # Ответственный за помещение — пользователь с профилем
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.SET_NULL, null=True,
                                    blank=True,
                                    related_name="responsible_rooms")
    responsible_phone = models.CharField(max_length=50,
                                         blank=True)  # дублирование для быстрого просмотра

    class Meta:
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"
        ordering = ["center__name", "name"]
        unique_together = [
            ("center", "name")]  # в рамках центра названия уникальны

    def __str__(self):
        return f"{self.center.name} — {self.name}"


class Status(models.TextChoices):
    PENDING = "PENDING", "В ожидании"
    APPROVED = "APPROVED", "Одобрено"
    REJECTED = "REJECTED", "Отклонено"
    CANCELED = "CANCELED", "Отменено"


class Booking(models.Model):
    """
    Бронирование помещения.
    - PENDING: заявка отправлена, не блокируем параллельные заявки
    - APPROVED: одобрено, блокируем пересечения по room+time_slot
    - REJECTED: отклонено, указываем причину
    - CANCELED: отменено пользователем/админом
    """

    room = models.ForeignKey(Room, on_delete=models.CASCADE,
                             related_name="bookings")
    time_slot = DateTimeRangeField()  # [start, end)
    status = models.CharField(max_length=10, choices=Status.choices,
                              default=Status.PENDING)

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="bookings"
    )
    # Новый идентификатор заявителя из Telegram (stateless)
    applicant_telegram_id = models.BigIntegerField(null=True, blank=True, db_index=True)

    applicant_name = models.CharField(max_length=255)
    applicant_phone = models.CharField(max_length=50)
    applicant_telegram_username = models.CharField(max_length=255, blank=True)

    comment = models.TextField(blank=True)

    # При отклонении — обязательная причина
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

    def approve(self):
        # Доп. проверка на пересечение перед утверждением
        if Booking.objects.filter(
                room=self.room,
                status=Status.APPROVED,
                time_slot__overlap=(self.start_at, self.end_at)
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Невозможно одобрить: пересечение с другой одобренной бронью.")
        self.status = Status.APPROVED
        self.full_clean()
        self.save(update_fields=["status", "updated_at"])

    def __str__(self):
        return f"{self.room} | {self.status} | {self.start_at} - {self.end_at}"

    @property
    def start_at(self):
        return self.time_slot.lower  # нижняя граница

    @property
    def end_at(self):
        return self.time_slot.upper  # верхняя граница (исключительно)

    def clean(self):
        # Базовая валидация диапазона
        if self.time_slot is None or self.start_at is None or self.end_at is None:
            raise ValidationError("Укажите корректный интервал времени.")
        if self.end_at <= self.start_at:
            raise ValidationError(
                "Время окончания должно быть позже времени начала.")

        # if (self.end_at - self.start_at) > datetime.timedelta(days=1):
        #     raise ValidationError("Длительность брони не должна превышать 1 день.")

    def approve(self):
        """
        Одобрение брони. Пересечения проверяются на уровне БД (constraint).
        """
        self.status = Status.APPROVED
        self.full_clean()
        self.save(update_fields=["status", "updated_at"])

    def reject(self, reason: str):
        if not reason:
            raise ValidationError("Укажите причину отклонения.")
        self.status = Status.REJECTED
        self.rejection_reason = reason
        self.save(update_fields=["status", "rejection_reason", "updated_at"])
