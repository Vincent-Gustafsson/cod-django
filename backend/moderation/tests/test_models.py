from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.backends.sqlite3.base import IntegrityError

from articles.models import Article, Comment

from ..models import Report


User = get_user_model()


class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user1',
            email='user1@gmail.com',
            password='password12345'
        )

        self.reporting_user = User.objects.create_user(
            username='reporting_user',
            email='reporting_user@gmail.com',
            password='password12345'
        )

        self.article = Article.objects.create(
            title='Test Article',
            content='content 123',
            user=self.user
        )

        self.comment = Comment.objects.create(
            body='Test Comment',
            article=self.article,
            user=self.user
        )

    def test_report_article(self):
        """ Reports an article. """
        article_report = Report.objects.create(
            reason=0,
            article=self.article,
            reported_by=self.reporting_user
        )

        self.assertTrue(isinstance(article_report, Report))
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(self.article.reports_count, 1)

    def test_report_comment(self):
        """ Reports a comment. """
        comment_report = Report.objects.create(
            reason=0,
            comment=self.comment,
            reported_by=self.reporting_user
        )

        self.assertTrue(isinstance(comment_report, Report))
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(self.comment.reports_count, 1)

    def test_report_user(self):
        """ Reports a user. """
        user_report = Report.objects.create(
            reason=0,
            user=self.user,
            reported_by=self.reporting_user
        )

        self.assertTrue(isinstance(user_report, Report))
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(self.user.reports_count, 1)

    def test_report_multiple_objects(self):
        """ Only one type of object can be reported per report. """
        report_obj = Report(
            article=self.article,
            comment=self.comment,
            reported_by=self.reporting_user
        )

        with self.assertRaises(Exception) as raised:
            report_obj.save()
            self.assertEqual(IntegrityError, type(raised.exception))
