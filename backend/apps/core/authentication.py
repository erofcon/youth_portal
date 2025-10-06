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


class TelegramUserPrincipal:
    """Лёгкий пользователь без записи в БД."""

    def __init__(self, data: dict):
        self.telegram_id = int(data["id"])
        self.username = data.get("username")  # без префикса tg_
        self.first_name = data.get("first_name", "")
        self.last_name = data.get("last_name", "")

    @property
    def is_authenticated(self):
        return True

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        handle = f"@{self.username}" if self.username else f"id:{self.telegram_id}"
        return f"TelegramUser({handle})"


class TelegramAuthentication(BaseAuthentication):
    keyword = 'Tma'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        try:
            auth_type, init_data_str = auth_header.split(' ')
        except ValueError:
            return None
        if auth_type.lower() != self.keyword.lower():
            return None

        is_valid, user_data = self.validate_init_data(init_data_str)
        if not is_valid:
            raise AuthenticationFailed('Invalid initData or data is outdated.')

        # В зависимости от настроек: создаём Django-пользователя или работаем stateless
        if getattr(settings, "TELEGRAM_CREATE_USER", False):
            user = self.get_or_create_user(user_data)
            return user, None

        # Stateless режим — не сохраняем, возвращаем “принципала”
        return TelegramUserPrincipal(user_data), None

    def validate_init_data(self, init_data_str: str) -> (bool, dict):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            if settings.DEBUG:
                try:
                    params = dict(p.split('=') for p in init_data_str.split('&'))
                    user_json = unquote(params['user'])
                    user_data = json.loads(user_json)
                    return True, user_data
                except Exception:
                    return False, {}
            return False, {}

        try:
            params = dict(p.split('=') for p in init_data_str.split('&'))
            hash_from_telegram = params.pop('hash')

            auth_date = int(params.get('auth_date', 0))
            if datetime.fromtimestamp(auth_date) < datetime.now() - timedelta(hours=1):
                raise AuthenticationFailed('Authentication data is outdated.')

            data_check_string = "\n".join(
                f"{key}={unquote(value)}" for key, value in sorted(params.items())
            )

            secret_key = hmac.new(
                "WebAppData".encode(), bot_token.encode(), hashlib.sha256
            ).digest()
            calculated_hash = hmac.new(
                secret_key, data_check_string.encode(), hashlib.sha256
            ).hexdigest()

            if calculated_hash != hash_from_telegram:
                return False, {}

            user_json = unquote(params['user'])
            user_data = json.loads(user_json)
            return True, user_data

        except Exception:
            return False, {}

    def get_or_create_user(self, user_data: dict):
        """Режим, когда хотим сохранять пользователей (можно включить флагом)."""
        tg_id = user_data['id']
        tg_username = user_data.get('username')
        preferred_username = f"tg_{tg_username}" if tg_username else f"tg_{tg_id}"
        legacy_username = f"tg_{tg_id}"

        # Ищем по preferred, потом по legacy; при наличии username — переименуем legacy в preferred
        try:
            user = User.objects.get(username=preferred_username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=legacy_username)
                if tg_username and not User.objects.filter(username=preferred_username).exists():
                    user.username = preferred_username
                    user.save(update_fields=['username'])
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=preferred_username,
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', '')
                )
                user.set_unusable_password()
                user.save()

        # Обновим ФИО
        changed = False
        if user.first_name != user_data.get('first_name', ''):
            user.first_name = user_data.get('first_name', '')
            changed = True
        if user.last_name != user_data.get('last_name', ''):
            user.last_name = user_data.get('last_name', '')
            changed = True
        if changed:
            user.save(update_fields=['first_name', 'last_name'])

        # Если у него есть профиль — сохраним chat_id (id Telegram)
        profile = getattr(user, 'profile', None)
        if profile:
            tg_id_str = str(tg_id)
            if profile.telegram_chat_id != tg_id_str:
                profile.telegram_chat_id = tg_id_str
                profile.save(update_fields=['telegram_chat_id'])

        return user
