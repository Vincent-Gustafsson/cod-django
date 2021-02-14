from django.db import models


class ArticleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(draft=False)


class ArticleDraftsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(draft=True)


class ArticleSlugsManager(models.Manager):
    """
    This manager is used by the AutoSlugField Field and is not
    supposed to be used anywhere else.
    """
    def get_queryset(self):
        return super().get_queryset().all()