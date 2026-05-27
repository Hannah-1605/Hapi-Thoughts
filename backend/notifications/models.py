# notifications/models.py

from django.db import models


class NotificationPreference(models.Model):
    # --- Relationship ---
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notification_preference",
    )

    # --- Email toggles ---
    email_appointment_reminders = models.BooleanField(default=True)
    email_appointment_status = models.BooleanField(default=True)
    email_billing = models.BooleanField(default=True)
    email_vaccination = models.BooleanField(default=True)
    email_followup = models.BooleanField(default=True)

    # --- Reminder timing ---
    appointment_reminder_days = models.IntegerField(default=1)
    vaccination_reminder_days = models.IntegerField(default=7)

    # --- Timestamps ---
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification preferences — {self.user.email}"
