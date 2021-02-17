from django.test import TestCase
from django.contrib.auth import get_user_model

from articles.models import Article, Comment

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

        self.comment = Comment.objects.create(
            body='test',
            article=self.article,
            user=self.user
        )

        self.reply = Comment.objects.create(
            body='test reply',
            article=self.article,
            parent=self.comment,
            user=self.user
        )

    def test_create_like_notification(self):
        """ Creates a like notification. """
        like_notification = Notification.objects.create(
            sender=self.user,
            action=Notification.LIKE,
            article=self.article
        )

        self.assertIsInstance(like_notification, Notification)
        self.assertEqual(
            like_notification.text_preview,
            f'{like_notification.sender} liked {like_notification.article.title}'
        )

    def test_create_special_like_notification(self):
        """ Creates a special like notification. """
        special_like_notification = Notification.objects.create(
            sender=self.user,
            action=Notification.SPECIAL_LIKE,
            article=self.article
        )

        self.assertIsInstance(special_like_notification, Notification)
        self.assertEqual(
            special_like_notification.text_preview,
            f'{special_like_notification.sender} Special liked {special_like_notification.article.title}'
        )

    def test_create_comment_notification(self):
        """ Creates a comment notification. """
        comment_notification = Notification.objects.create(
            sender=self.user,
            action=Notification.COMMENT,
            comment=self.comment
        )

        self.assertIsInstance(comment_notification, Notification)
        self.assertEqual(
            comment_notification.text_preview,
            f'{comment_notification.sender} commented on {comment_notification.comment.article.title}'
        )

    def test_create_reply_notification(self):
        """ Creates a reply notification. """
        reply_notification = Notification.objects.create(
            sender=self.user,
            action=Notification.REPLY,
            comment=self.reply
        )

        self.assertIsInstance(reply_notification, Notification)
        self.assertEqual(
            reply_notification.text_preview,
            f'{reply_notification.sender} replied to {reply_notification.comment.body[:20]}...'
        )

    def test_create_follow_notification(self):
        """ Creates a follow notification. """
        follow_notification = Notification.objects.create(
            sender=self.user,
            action=Notification.FOLLOW,
            user=self.user_2
        )

        self.assertIsInstance(follow_notification, Notification)
        self.assertEqual(
            follow_notification.text_preview,
            f'{follow_notification.sender} is now following you'
        )
