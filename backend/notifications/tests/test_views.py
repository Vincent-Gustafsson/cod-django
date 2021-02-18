from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Article, Comment

from ..models import Notification
from ..serializers import NotificationSerializer


User = get_user_model()


class NotificationViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            email='test_user@gmail.com',
            password='12345'
        )

        self.user_2 = User.objects.create_user(
            username='test_user_2',
            email='test_user_2@gmail.com',
            password='12345'
        )

        self.article = Article.objects.create(
            title='Test',
            content="test 123",
            user=self.user,
        )

        self.comment = Comment.objects.create(
            body='test_comment',
            article=self.article,
            user=self.user,
        )

        self.like_notification = Notification(
            sender=self.user_2,
            action=Notification.LIKE,
            article=self.article
        )

        self.follow_notification = Notification(
            sender=self.user_2,
            action=Notification.FOLLOW,
            user=self.user
        )

    def test_get_all_notifications(self):
        """ Returns all the user's notifications. """
        self.like_notification.save()
        self.follow_notification.save()

        url = reverse('notification-list')

        self.client.force_authenticate(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json()['results']), 3)

    def test_mark_all_notifications(self):
        """ Mark all the user's notifications as seen. """
        self.like_notification.save()
        self.follow_notification.save()

        url = reverse('notification-mark-all')

        self.client.force_authenticate(self.user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Notification.objects.filter(seen=True).count(), 3)

    def test_mark_notification(self):
        """ Mark supplied notification as seen. """
        url = reverse('notification-mark', kwargs={'pk': Notification.objects.get().id})

        self.client.force_authenticate(self.user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Notification.objects.filter(seen=True).count(), 1)
