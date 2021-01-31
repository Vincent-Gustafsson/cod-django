from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from .models import Article

@receiver(m2m_changed, sender=Article.tags.through)
def tags_changed(sender, **kwargs):
    if kwargs['instance'].tags.count() > 5:
        raise ValidationError("You can't assign more than five tags")
