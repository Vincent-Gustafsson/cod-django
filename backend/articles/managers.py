from django.db import models


class ArticleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(draft=False)

class ArticleDraftsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(draft=True)