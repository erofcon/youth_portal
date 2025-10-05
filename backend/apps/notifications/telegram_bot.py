import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id: str, text: str) -> bool:
    """
    Отправляет сообщение в Telegram чат.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не установлен в настройках.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
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
        return False
