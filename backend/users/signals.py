from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import User

@receiver(pre_save, sender=User)
def set_display_name(sender, instance, **kwargs):
    # If display_name is None set display_name to the username
    # This is used to set the display_name to the username when the account is created.
    # Display name will prbably be set by the user when he / she updates their profile.
    if instance.display_name == None:
        instance.display_name = instance.username
        instance.save()