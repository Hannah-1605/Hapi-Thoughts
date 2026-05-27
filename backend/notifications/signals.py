# notifications/signals.py

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import NotificationPreference

User = get_user_model()


@receiver(post_save, sender=User)
def create_notification_preference(sender, instance, created, **kwargs):
    """
    Auto-creates a NotificationPreference row whenever a new User is created.
    Runs for both Admin and Pet Owner — defaults are the same for both.
    """
    if created:
        NotificationPreference.objects.create(user=instance)
