# apps/core/authentication.py

import hmac
import hashlib
import json
from urllib.parse import unquote
from datetime import datetime, timedelta

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class TelegramAuthentication(BaseAuthentication):
    """
    Кастомная аутентификация для Telegram Mini Apps.
    Проверяет подлинность данных, переданных в заголовке Authorization: Tma <initData>.
    """
    keyword = 'Tma'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None  # Аутентификация не предоставлена

        try:
            auth_type, init_data_str = auth_header.split(' ')
        except ValueError:
            return None  # Неверный формат заголовка

        if auth_type.lower() != self.keyword.lower():
            return None  # Не наш тип аутентификации

        # Валидируем initData
        is_valid, user_data = self.validate_init_data(init_data_str)

        if not is_valid:
            raise AuthenticationFailed('Invalid initData or data is outdated.')

        # Находим или создаем пользователя
        user = self.get_or_create_user(user_data)

        return user, None  # (user, auth) - успешная аутентификация

    def validate_init_data(self, init_data_str: str) -> (bool, dict):
        """
        Валидирует строку initData, полученную от Telegram.
        https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
        """
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            # В DEV режиме можно пропускать проверку, если токен не задан
            if settings.DEBUG:
                try:
                    # Попытаемся разобрать данные без проверки подписи
                    params = dict(
                        p.split('=') for p in init_data_str.split('&'))
                    user_json = unquote(params['user'])
                    user_data = json.loads(user_json)
                    return True, user_data
                except Exception:
                    return False, {}
            return False, {}

        try:
            # Сортируем параметры и готовим строку для проверки
            params = dict(p.split('=') for p in init_data_str.split('&'))
            hash_from_telegram = params.pop('hash')

            # Проверяем, что данные не устарели (например, старше 1 часа)
            auth_date = int(params.get('auth_date', 0))
            if datetime.fromtimestamp(auth_date) < datetime.now() - timedelta(
                    hours=1):
                raise AuthenticationFailed('Authentication data is outdated.')

            # Формируем строку для проверки хеша
            data_check_string = "\n".join(
                f"{key}={unquote(value)}" for key, value in
                sorted(params.items())
            )

            # Вычисляем хеш
            secret_key = hmac.new(
                "WebAppData".encode(), bot_token.encode(), hashlib.sha256
            ).digest()
            calculated_hash = hmac.new(
                secret_key, data_check_string.encode(), hashlib.sha256
            ).hexdigest()

            # Сравниваем хеши
            if calculated_hash != hash_from_telegram:
                return False, {}

            # Если всё хорошо, извлекаем данные пользователя
            user_json = unquote(params['user'])
            user_data = json.loads(user_json)

            return True, user_data

        except Exception:
            return False, {}

    def get_or_create_user(self, user_data: dict):
        """
        Находит пользователя по telegram_id или создает нового.
        """
        telegram_id = user_data['id']
        username = f"tg_{telegram_id}"

        try:
            user = User.objects.get(username=username)
            # Опционально: обновляем данные пользователя при каждом входе
            user.first_name = user_data.get('first_name', '')
            user.last_name = user_data.get('last_name', '')
            user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', '')
            )
            # Пароль не нужен, так как вход только через Telegram
            user.set_unusable_password()
            user.save()

        return user
