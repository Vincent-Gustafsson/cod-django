from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse

from autoslug import AutoSlugField

from .managers import MyUserManager


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    display_name = models.CharField(max_length=30, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)

    slug = AutoSlugField(null=True, default=None, unique=True, populate_from='username')

    avatar = models.ImageField(upload_to='uploads/avatars',
                               default='uploads/avatars/default_avatar.png')

    saved_articles = models.ManyToManyField('articles.Article', related_name='saves',
                                            blank=True)

    date_joined = models.DateField(verbose_name='date joined', auto_now_add=True)

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['email']

    objects = MyUserManager()

    def __str__(self):
        return self.username

    @property
    def reports_count(self):
        return self.reports.count()

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'slug': self.slug})

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class UserFollowing(models.Model):
    user_follows = models.ForeignKey('User', related_name="following", on_delete=models.CASCADE)
    user_followed = models.ForeignKey('User', related_name="followers", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user_follows', 'user_followed'],
                name="unique_followers"
            )
        ]

    def __str__(self):
        return f'{self.user_follows} follows {self.user_followed}'
