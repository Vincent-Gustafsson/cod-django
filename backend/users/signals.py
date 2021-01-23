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
    
    if instance.avatar == None:
        # Gets the default value of the avatar ImageField.
        # In this case:
        #   ImageField(upload_to='uploads/avatars', default='uploads/avatars/default_avatar.png')
        #
        # default_avatar_path will be equal to 'uploads/avatars/default_avatar.png'

        default_avatar_path = User._meta.get_field('avatar').get_default()
        instance.avatar = default_avatar_path
        instance.save()
    