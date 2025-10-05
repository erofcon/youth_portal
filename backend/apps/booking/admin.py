from django.contrib import admin, messages
from django.db import transaction
from .models import RoomTag, Room, Booking, Status


# Ограничение видимости данных для ответственных
class OwnerRestrictedAdminMixin:
    """
    Если пользователь не суперюзер — показываем только объекты, связанные с ним.
    Для комнат: room.responsible = request.user
    Для броней: booking.room.responsible = request.user
    """

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if self.model is Room:
            return qs.filter(responsible=request.user)
        if self.model is Booking:
            return qs.filter(room__responsible=request.user)
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Ограничим выбор помещения для брони только своими
        if db_field.name == "room" and not request.user.is_superuser:
            kwargs["queryset"] = Room.objects.filter(responsible=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(RoomTag)
class RoomTagAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Room)
class RoomAdmin(OwnerRestrictedAdminMixin, admin.ModelAdmin):
    list_display = ["name", "center", "capacity", "responsible",
                    "responsible_phone", "tags_list"]
    list_filter = ["center", "tags"]
    search_fields = ["name", "description"]
    filter_horizontal = ["tags"]

    def tags_list(self, obj):
        return ", ".join(obj.tags.values_list("name", flat=True))


@admin.register(Booking)
class BookingAdmin(OwnerRestrictedAdminMixin, admin.ModelAdmin):
    list_display = ["id", "room", "status", "interval", "applicant_name",
                    "applicant_phone", "created_at"]
    list_filter = ["status", "room__center"]
    search_fields = ["applicant_name", "applicant_phone", "comment",
                     "rejection_reason"]
    readonly_fields = ["created_at", "updated_at"]

    actions = ["approve_selected", "reject_selected_with_reason"]

    def interval(self, obj):
        return f"{obj.start_at} — {obj.end_at}"

    @admin.action(description="Одобрить выбранные бронирования")
    def approve_selected(self, request, queryset):
        with transaction.atomic():
            ok, fail = 0, 0
            for booking in queryset.select_for_update():
                try:
                    booking.approve()
                    ok += 1
                except Exception as e:
                    fail += 1
            self.message_user(request, f"Одобрено: {ok}, ошибок: {fail}",
                              level=messages.INFO)

    @admin.action(description="Отклонить с причиной")
    def reject_selected_with_reason(self, request, queryset):
        """
        Простой вариант: отклоняем со статичной причиной.
        Можно доработать через промежуточную форму для ввода причины.
        """
        reason = "Забронировано в это время / не подходит по условиям."
        updated = 0
        for booking in queryset:
            if booking.status == Status.PENDING:
                booking.reject(reason)
                updated += 1
        self.message_user(request, f"Отклонено заявок: {updated}",
                          level=messages.WARNING)
