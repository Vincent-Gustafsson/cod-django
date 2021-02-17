from django.test import TestCase
from django.contrib.auth import get_user_model

from articles.models import Article, ArticleLike, Comment
from users.models import UserFollowing

from ..models import Notification

User = get_user_model()


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            email='test_user@gmail.com',
            password='12345'
        )

        self.user_2 = User.objects.create_user(
            username='test_user2',
            email='test_user2@gmail.com',
            password='12345'
        )

        self.article = Article.objects.create(
            title='Test',
            content="test content",
            user=self.user
        )

        self.comment = Comment(
            body='test',
            article=self.article,
            user=self.user
        )

        self.reply = Comment(
            body='test reply',
            article=self.article,
            parent=self.comment,
            user=self.user
        )

        self.article_like = ArticleLike(
            user=self.user_2,
            article=self.article
        )

        self.special_article_like = ArticleLike(
            special_like=True,
            user=self.user_2,
            article=self.article
        )

        self.follow = UserFollowing(
            user_follows=self.user,
            user_followed=self.user_2
        )

    def test_create_like_notification_via_signal(self):
        """ Creates a like notification via the signal. """
        self.article_like.save()

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(
            str(Notification.objects.get()),
            f'{self.user_2.display_name} liked {self.article.title}'
        )

    def test_create_special_like_notification_via_signal(self):
        """ Creates a special like notification via the signal. """
        self.special_article_like.save()

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(
            str(Notification.objects.get()),
            f'{self.user_2.display_name} Special liked {self.article.title}'
        )

    def test_create_comment_notification_via_signal(self):
        """ Creates a comment notification via the signal. """
        self.comment.save()

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(
            str(Notification.objects.get()),
            f'{self.user.display_name} commented on {self.article.title}'
        )

    def test_create_reply_notification_via_signal(self):
        """ Creates a reply notification via the signal. """
        self.comment.save()
        self.reply.save()

        self.assertEqual(Notification.objects.count(), 3)
        self.assertEqual(
            str(Notification.objects.get(action=Notification.REPLY)),
            f'{self.user.display_name} replied to {self.reply.body}...'
        )

    def test_create_follow_notification_via_signal(self):
        """ Creates a follow notification via the signal. """
        self.follow.save()

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(
            str(Notification.objects.get()),
            f'{self.user.display_name} is now following you'
        )
