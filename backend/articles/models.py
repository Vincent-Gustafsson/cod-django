from django.db import models
from django.contrib.auth import get_user_model


class Article(models.Model):
    title = models.CharField(50)
    content = models.TextField()
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='articles')

    # likes
    # special_likes

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title[:10]}...'


class Comment(models.Model):
    body = models.CharField(300)

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='comments')
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='comments')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.body[10]}...'

    @property
    def get_score(self):
        votes = self.comment_votes.all()
        if votes[0]:
            return votes.filter(downvote=False) - votes.filter(downvote=True)

        return 0


class CommentVote(models.Model):
    downvote = models.BooleanField(default=False)

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='comment_votes')
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='comment_votes')

    def __str__(self):
        if not self.downvote:
            return f'{self.user.username} upvoted {self.comment.body[:10]}...'
        else:
            return f'{self.user.username} downvoted {self.comment.body[:10]}...'