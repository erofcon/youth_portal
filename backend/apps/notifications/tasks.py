from celery import shared_task
import logging

# from apps.booking.models import Booking, Status
# Обновляем импорт
from apps.booking.models import Booking, Status
from .telegram_bot import send_message_to_admin, send_message_to_user

logger = logging.getLogger(__name__)


def _format_booking_details(booking: Booking) -> str:
    """Вспомогательная функция для форматирования деталей брони."""
    start_time = booking.start_at.strftime('%d.%m.%Y в %H:%M')
    end_time = booking.end_at.strftime('%H:%M')
    return (
        f"<b>Помещение:</b> {booking.room.center.name} - {booking.room.name}\n"
        f"<b>Время:</b> с {start_time} до {end_time}"
    )


@shared_task
def notify_responsible_of_new_booking(booking_id: int):
    """
    Задача для отправки уведомления ответственному о новом бронировании.
    (Использует бот для администраторов)
    """
    try:
        booking = Booking.objects.select_related(
            'room', 'room__responsible', 'room__responsible__profile'
        ).get(id=booking_id)
    except Booking.DoesNotExist:
        logger.warning(f"Бронирование с ID {booking_id} не найдено.")
        return

    responsible_user = booking.room.responsible
    if not responsible_user or not hasattr(responsible_user,
                                           'profile') or not responsible_user.profile.telegram_chat_id:
        logger.warning(
            f"У ответственного за помещение '{booking.room.name}' не найден chat_id. "
            f"Уведомление о бронировании {booking_id} не отправлено."
        )
        return

    chat_id = responsible_user.profile.telegram_chat_id
    details = _format_booking_details(booking)
    message = (
        f"🔔 <b>Новая заявка на бронирование!</b>\n\n"
        f"{details}\n"
        f"<b>Заявитель:</b> {booking.applicant_name}\n"
        f"<b>Телефон:</b> {booking.applicant_phone or 'не указан'}\n\n"
        f"<i>Для одобрения или отклонения, пожалуйста, перейдите в админ-панель.</i>"
    )

    # ИЗМЕНЕНО: Используем новую явную функцию
    send_message_to_admin(chat_id, message)


# --- НОВЫЕ ЗАДАЧИ ДЛЯ УВЕДОМЛЕНИЯ ПОЛЬЗОВАТЕЛЕЙ ---

def _notify_user(booking_id: int, message_template: str):
    """Общая логика для отправки уведомления пользователю."""
    try:
        booking = Booking.objects.select_related('room', 'room__center').get(
            id=booking_id)
    except Booking.DoesNotExist:
        return  # Ошибку логировать не будем, т.к. может быть удалено

    if not booking.applicant_telegram_id:
        logger.info(
            f"Для брони {booking_id} не указан applicant_telegram_id. Уведомление пользователю не отправлено.")
        return

    details = _format_booking_details(booking)
    message = message_template.format(details=details, booking=booking)
    send_message_to_user(str(booking.applicant_telegram_id), message)


@shared_task
def notify_user_of_pending_booking(booking_id: int):
    """Уведомление пользователю о том, что его заявка принята в обработку."""
    message_template = (
        "✅ <b>Ваша заявка принята!</b>\n\n"
        "{details}\n\n"
        "Мы сообщим вам, как только администратор рассмотрит её."
    )
    _notify_user(booking_id, message_template)


@shared_task
def notify_user_of_approved_booking(booking_id: int):
    """Уведомление пользователю об одобрении брони."""
    message_template = (
        "🎉 <b>Ваша заявка одобрена!</b>\n\n"
        "{details}\n\n"
        "Помещение забронировано за вами. Хорошего мероприятия!"
    )
    _notify_user(booking_id, message_template)


@shared_task
def notify_user_of_rejected_booking(booking_id: int):
    """Уведомление пользователю об отклонении брони."""
    message_template = (
        "😔 <b>Ваша заявка отклонена.</b>\n\n"
        "{details}\n\n"
        "<b>Причина:</b> {booking.rejection_reason}\n\n"
        "Пожалуйста, попробуйте выбрать другое время или помещение."
    )
    _notify_user(booking_id, message_template)
