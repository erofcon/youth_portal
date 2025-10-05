from django.db import models

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class District(models.Model):
    """Район (например, Черекский, Эльбрусский и т.д.)."""
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class YouthCenter(models.Model):
    """Молодёжный центр в районе."""
    district = models.ForeignKey(District, on_delete=models.CASCADE,
                                 related_name="centers")
    name = models.CharField(max_length=255, unique=True)
    emblem = models.ImageField(upload_to="centers/emblems/", blank=True,
                               null=True)  # Герб/логотип

    address = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    responsible_name = models.CharField(max_length=255,
                                        blank=True)  # Руководитель центра

    responsible_phone = models.CharField(max_length=50, blank=True)
    responsible_telegram_chat_id = models.CharField(max_length=64,
                                                    blank=True)  # Для уведомлений центра (опционально)

    class Meta:
        verbose_name = "Молодёжный центр"
        verbose_name_plural = "Молодёжные центры"
        ordering = ["district__name", "name"]

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Профиль сотрудника (для ответственных и администратора).
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name="profile")

    center = models.ForeignKey(YouthCenter, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name="staff")

    phone = models.CharField(max_length=50, blank=True)
    telegram_chat_id = models.CharField(max_length=64,
                                        blank=True)  # Куда слать уведомления
    # Роль(например, руководитель центра)
    ROLE_CHOICES = (
        ("ADMIN", "Администратор"),
        ("RESP", "Ответственный за помещение"),
        ("CENTER", "Руководитель центра"),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="RESP")

    class Meta:
        verbose_name = "Профиль сотрудника"
        verbose_name_plural = "Профили сотрудников"

    def __str__(self):
        return f"{self.user.username} ({self.role})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
