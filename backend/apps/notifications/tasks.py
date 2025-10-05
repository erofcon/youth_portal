from celery import shared_task
import logging

from apps.booking.models import Booking
from .telegram_bot import send_telegram_message

logger = logging.getLogger(__name__)


@shared_task
def notify_responsible_of_new_booking(booking_id: int):
    """
    Задача для отправки уведомления ответственному о новом бронировании.
    """
    try:
        booking = Booking.objects.select_related(
            'room', 'room__responsible', 'room__responsible__profile'
        ).get(id=booking_id)
    except Booking.DoesNotExist:
        logger.warning(f"Бронирование с ID {booking_id} не найдено.")
        return

    responsible_user = booking.room.responsible
    if not responsible_user:
        logger.info(
            f"Для помещения '{booking.room.name}' не назначен ответственный. Уведомление не отправлено.")
        return

    # Проверяем, есть ли у пользователя профиль и chat_id
    if not hasattr(responsible_user,
                   'profile') or not responsible_user.profile.telegram_chat_id:
        logger.warning(
            f"У ответственного {responsible_user.username} не указан telegram_chat_id в профиле. "
            f"Уведомление о бронировании {booking_id} не отправлено."
        )
        return

    chat_id = responsible_user.profile.telegram_chat_id

    # Формируем сообщение
    start_time = booking.start_at.strftime('%d.%m.%Y в %H:%M')
    end_time = booking.end_at.strftime('%H:%M')

    message = (
        f"🔔 <b>Новая заявка на бронирование!</b>\n\n"
        f"<b>Помещение:</b> {booking.room.center.name} - {booking.room.name}\n"
        f"<b>Время:</b> с {start_time} до {end_time}\n"
        f"<b>Заявитель:</b> {booking.applicant_name}\n"
        f"<b>Телефон:</b> {booking.applicant_phone}\n\n"
        f"<i>Для одобрения или отклонения, пожалуйста, перейдите в админ-панель.</i>"
    )

    send_telegram_message(chat_id, message)
