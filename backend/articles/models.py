from django.db import models
from django.contrib.auth import get_user_model


class Article(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='articles')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title[:20]}...'

    @property
    def likes_count(self):
        likes = self.likes.all()
        return likes.filter(article=self, special_like=False).count()

    @property
    def special_likes_count(self):
        likes = self.likes.all()
        return likes.filter(article=self, special_like=True).count()

    @property
    def comments_count(self):
        return Comment.objects.filter(article=self).count()

    @property
    def saved_count(self):
        return self.saves.count()


class ArticleLike(models.Model):
    special_like = models.BooleanField(default=False)

    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             related_name='article_likes')

    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='likes')

    def __str__(self):
        if not self.special_like:
            return f'{self.user.username} liked {self.article.title[:20]}...'
        else:
            return f'{self.user.username} special-liked {self.article.title[:20]}...'


class Comment(models.Model):
    body = models.CharField(max_length=300)

    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='comments')
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='comments')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.body[:20]}...'

    def save(self, *args, **kwargs):
        if self.deleted:
            self.body = 'deleted'
            self.user = None

        super(Comment, self).save(*args, **kwargs)

    @property
    def score(self):
        votes = self.comment_votes.all()
        if votes:
            return votes.filter(downvote=False).count() - votes.filter(downvote=True).count()

        return 0


class CommentVote(models.Model):
    downvote = models.BooleanField(default=False)

    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             related_name='comment_votes')

    comment = models.ForeignKey('Comment',
                                on_delete=models.CASCADE,
                                related_name='comment_votes')

    def __str__(self):
        if not self.downvote:
            return f'{self.user.username} upvoted {self.comment.body[:20]}...'
        else:
            return f'{self.user.username} downvoted {self.comment.body[:20]}...'
