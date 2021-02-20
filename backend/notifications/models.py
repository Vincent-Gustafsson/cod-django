from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Notification(models.Model):
    LIKE = 0
    SPECIAL_LIKE = 1
    COMMENT = 2
    REPLY = 3
    FOLLOW = 4

    ACTIONS = (
        (LIKE, 'Like'),
        (SPECIAL_LIKE, 'Special like'),

        (COMMENT, 'Comment'),
        (REPLY, 'Reply'),

        (FOLLOW, 'Follow')
    )

    action = models.IntegerField(choices=ACTIONS)    

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notice_from_user")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")

    article = models.ForeignKey(
        'articles.Article',
        on_delete=models.CASCADE,
        related_name="notice_article",
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notice_user",
        blank=True,
        null=True
    )
    comment = models.ForeignKey(
        'articles.Comment',
        on_delete=models.CASCADE,
        related_name="notice_comment",
        blank=True,
        null=True
    )

    preview_text = models.CharField(max_length=100, blank=True, null=True)
    seen = models.BooleanField(default=False)

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

    def __generate_details_text(self):
        if self.article:
            if self.action == self.LIKE:
                return f'{self.sender.display_name} liked {self.article.title}'
            elif self.action == self.SPECIAL_LIKE:
                return f'{self.sender.display_name} Special liked {self.article.title}'

        if self.comment:
            if self.action == self.COMMENT:
                return f'{self.sender.display_name} commented on {self.comment.article.title}'
            elif self.action == self.REPLY:
                return f'{self.sender.display_name} replied to {self.comment.body[:20]}...'

        if self.user:
            if self.action == self.FOLLOW:
                return f'{self.sender.display_name} is now following you'

    def __str__(self):
        return self.__generate_details_text()

    def save(self, *args, **kwargs):
        self.preview_text = self.__generate_details_text()

        if self.article:
            self.receiver = self.article.user

        elif self.comment:
            if self.action == self.COMMENT:
                self.receiver = self.comment.article.user

            elif self.action == self.REPLY:
                self.receiver = self.comment.parent.user

        elif self.user:
            self.receiver = self.user

        super(Notification, self).save(*args, **kwargs)
