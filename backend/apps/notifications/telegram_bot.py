import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def _send_message(bot_token: str, chat_id: str, text: str) -> bool:
    """Внутренняя функция для отправки сообщения через указанный токен."""
    if not bot_token:
        logger.error("Токен для Telegram-бота не предоставлен.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        logger.info(f"Сообщение успешно отправлено в чат {chat_id}")
        return True
    except requests.RequestException as e:
        logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")
        # Можно добавить логирование ответа от Telegram API для отладки
        if e.response:
            logger.error(f"Ответ от Telegram: {e.response.text}")
        return False


def send_message_to_user(chat_id: str, text: str) -> bool:
    """
    Отправляет сообщение пользователю через основной бот (для Mini App).
    """
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.error(
            "TELEGRAM_BOT_TOKEN не установлен. Уведомление пользователю не отправлено.")
        return False
    return _send_message(token, chat_id, text)


def send_message_to_admin(chat_id: str, text: str) -> bool:
    """
    Отправляет сообщение администратору/ответственному через бот для уведомлений.
    """
    # Использует NOTIFY токен, если он есть, иначе — основной
    token = settings.TELEGRAM_NOTIFY_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.error(
            "Ни TELEGRAM_NOTIFY_BOT_TOKEN, ни TELEGRAM_BOT_TOKEN не установлен. Уведомление администратору не отправлено.")
        return False
    return _send_message(token, chat_id, text)
