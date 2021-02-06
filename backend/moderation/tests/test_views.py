from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Article, Comment
from ..models import Report


User = get_user_model()


class ReportViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            email='test_user@gmail.com',
            password='password12345'
        )

        self.user_2 = User.objects.create_user(
            username='test_user2',
            email='test_user2@gmail.com',
            password='password12345'
        )

        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@gmail.com',
            password='password12345'
        )
        self.moderator.is_moderator = True
        self.moderator.save()

        self.article = Article.objects.create(
            title='Test article',
            content='Content 123',
            user=self.user_2
        )

        self.comment = Comment.objects.create(
            body='Test comment',
            article=self.article,
            user=self.user_2
        )

        self.report = Report(
            user=self.user_2,
            reported_by=self.user
        )

    def test_report_article(self):
        """
        Reports the given article.
        """
        url = reverse('report-list')

        data = {
            'message': 'This is offensive content.',
            'article': self.article.id
        }

        self.client.force_authenticate(self.user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)

    def test_report_comment(self):
        """
        Reports the given comment.
        """
        url = reverse('report-list')

        data = {
            'message': 'This is offensive content.',
            'comment': self.comment.id
        }

        self.client.force_authenticate(self.user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)

    def test_report_user(self):
        """
        Reports the given user.
        """
        url = reverse('report-list')

        data = {
            'message': 'This is offensive content.',
            'user': self.user_2.id
        }

        self.client.force_authenticate(self.user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)

    def test_report_own_article(self):
        """
        Disallows reporting your own article.
        """
        url = reverse('report-list')

        data = {
            'message': 'This is offensive content.',
            'article': self.article.id
        }

        self.client.force_authenticate(self.user_2)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'details': 'Can\'t report your own article.'})

        self.assertEqual(Report.objects.count(), 0)

    def test_report_own_comment(self):
        """
        Disallows reporting your own comment.
        """
        url = reverse('report-list')

        data = {
            'message': 'This is offensive content.',
            'comment': self.comment.id
        }

        self.client.force_authenticate(self.user_2)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'details': 'Can\'t report your own comment.'})

        self.assertEqual(Report.objects.count(), 0)

    def test_report_yourself(self):
        """
        Disallows reporting yourself.
        """
        url = reverse('report-list')

        data = {
            'message': 'This is offensive content.',
            'user': self.user_2.id
        }

        self.client.force_authenticate(self.user_2)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'details': 'Can\'t report yourself.'})

        self.assertEqual(Report.objects.count(), 0)

    def test_list_reports_authorized(self):
        """
        Granten access to list (GET) all reports
        because the user is a moderator.
        """
        url = reverse('report-list')

        self.client.force_authenticate(self.moderator)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_reports_unauthorized(self):
        """
        Denied access to list (GET) all reports
        because the user is not a moderator.
        """
        url = reverse('report-list')

        self.client.force_authenticate(self.user)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_report_moderated_authorized(self):
        """
        Marks report as moderated.
        """
        self.report.save()
        url = reverse('report-detail', kwargs={'pk': self.report.id})

        self.client.force_authenticate(self.moderator)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Report.objects.filter(moderated=True).count(), 1)

    def test_mark_report_moderated_unauthorized(self):
        """
        Denies access to marking as moderated if not a moderator.
        """
        self.report.save()
        url = reverse('report-detail', kwargs={'pk': self.report.id})

        self.client.force_authenticate(self.user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_moderated_reports(self):
        """
        Filter out unmoderated reports.
        """
        url = reverse('report-list') + '?moderated=True'

        for i in range(3):
            is_moderated = True if i == 1 else False
            Report.objects.create(
                article=self.article,
                reported_by=self.user_2,
                moderated=is_moderated
            )

        self.client.force_authenticate(self.moderator)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_list_unmoderated_reports(self):
        """
        Filter out moderated reports.
        """
        url = reverse('report-list')

        for i in range(3):
            is_moderated = True if i == 1 else False
            Report.objects.create(
                article=self.article,
                reported_by=self.user_2,
                moderated=is_moderated
            )

        self.client.force_authenticate(self.moderator)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_cant_set_moderated_on_creation(self):
        """
        Can't set the moderated field to True when creating a report.
        """
        url = reverse('report-list')

        data = {
            'article': self.article.id,
            'reported_by': self.user_2.id,
            'moderated': True
        }

        self.client.force_authenticate(self.user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Report.objects.get().moderated, False)
