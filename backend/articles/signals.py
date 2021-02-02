from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_400_BAD_REQUEST

from .models import Article


@receiver(m2m_changed, sender=Article.tags.through)
def tags_changed(sender, **kwargs):
    if kwargs['instance'].tags.count() > 5:
        raise ValidationError(
            {'details': 'You can\'t assign more than five tags'},
            code=HTTP_400_BAD_REQUEST
        )
