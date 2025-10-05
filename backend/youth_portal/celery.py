import os
from celery import Celery
from django.conf import settings

# Устанавливаем переменную окружения, чтобы celery знала о настройках Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youth_portal.settings')

app = Celery('youth_portal')

# Используем префикс 'CELERY_' для всех настроек в settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем и регистрируем задачи из всех файлов tasks.py в приложениях Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
