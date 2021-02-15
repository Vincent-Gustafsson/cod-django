from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_400_BAD_REQUEST

from notifications.models import Notification

from .models import Article, ArticleLike, Comment


@receiver(m2m_changed, sender=Article.tags.through)
def tags_changed(sender, **kwargs):
    if kwargs['instance'].tags.count() > 5:
        raise ValidationError(
            {'details': 'You can\'t assign more than five tags'},
            code=HTTP_400_BAD_REQUEST
        )


@receiver(post_save, sender=ArticleLike)
def send_like_notification(sender, instance, **kwargs):
    if instance.special_like:
        Notification.objects.create(
            sender=instance.user,
            receiver=instance.article.user,
            action=Notification.SPECIAL_LIKE,
            article=instance.article
        )

    else:
        Notification.objects.create(
            sender=instance.user,
            receiver=instance.article.user,
            action=Notification.LIKE,
            article=instance.article
        )


@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, **kwargs):
    # If the comment isn't deleted.
    if instance.user:
        Notification.objects.create(
            sender=instance.user,
            receiver=instance.article.user,
            action=Notification.COMMENT,
            comment=instance
        )

        if instance.parent:
            Notification.objects.create(
                sender=instance.user,
                receiver=instance.parent.user,
                action=Notification.REPLY,
                comment=instance
            )
