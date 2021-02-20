from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification

from .models import UserFollowing


@receiver(post_save, sender=UserFollowing)
def send_follow_notification(sender, instance, **kwargs):
    Notification.objects.create(
        sender=instance.user_follows,
        action=Notification.FOLLOW,
        user=instance.user_followed
    )
