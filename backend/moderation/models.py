from django.db import models


# I Could have used a GenericForeignKey in this situation but I chose not to.
# https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/
class Report(models.Model):
    RUDE_VULGAR = 0
    SPAM = 1
    COPYRIGHT = 2
    HARASSMENT_HATE_SPEECH = 3
    INAPPROPRIATE_CONTENT = 4
    OTHER = 5

    REASONS = (
        (RUDE_VULGAR, 'Rude or vulgar'),
        (SPAM, 'Spam'),
        (COPYRIGHT, 'Copyright issue'),
        (HARASSMENT_HATE_SPEECH, 'Harassment or hate speech'),
        (INAPPROPRIATE_CONTENT, 'Inappropriate content'),
        (OTHER, 'Other')
    )

    reason = models.IntegerField(choices=REASONS)

    message = models.CharField(max_length=500, blank=True, null=True)

    article = models.ForeignKey('articles.Article', models.CASCADE, related_name='reports',
                                blank=True, null=True)

    comment = models.ForeignKey('articles.Comment', models.CASCADE, related_name='reports',
                                blank=True, null=True)

    user = models.ForeignKey('users.User', models.CASCADE, related_name='reports',
                             blank=True, null=True)

    reported_by = models.ForeignKey('users.User', models.CASCADE)
    moderated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_object_only_one",
                check=(
                    models.Q(
                        article__isnull=False,
                        comment__isnull=True,
                        user__isnull=True,
                    )
                    | models.Q(
                        article__isnull=True,
                        comment__isnull=False,
                        user__isnull=True,
                    )
                    | models.Q(
                        article__isnull=True,
                        comment__isnull=True,
                        user__isnull=False,
                    )
                ),
            )
        ]

    def __str__(self):
        obj = None
        if self.article:
            obj = self.article
        elif self.comment:
            obj = self.comment
        else:
            obj = self.user

        return f'{self.reported_by.username} reported {obj}'

    @property
    def reported_object(self):
        if self.article:
            return self.article

        elif self.comment:
            return self.comment

        elif self.user:
            return self.user

        else:
            raise AssertionError("Error: no object is set.")
