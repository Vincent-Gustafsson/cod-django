from django.test import TestCase
from django.contrib.auth import get_user_model

import faker

from .models import Article, ArticleLike, Comment, CommentVote


fake = faker.Faker('en')
User = get_user_model()


class ArticleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=fake.first_name(),
            email=fake.email(),
            password=fake.password()
        )

        self.article = Article.objects.create(
            title='Test',
            content="test 123",
            user=self.user
        )

        self.normal_like = ArticleLike.objects.create(
            article=self.article,
            user=self.user
        )
        self.special_like = ArticleLike.objects.create(
            article=self.article,
            user=self.user,
            special_like=True
        )

    def test_create_user(self):
        self.assertTrue(isinstance(self.article, Article))
        self.assertEqual(str(self.article), f'{self.article.title[:10]}...')

    def test_likes_count(self):
        self.assertEqual(self.article.likes_count, 1)

    def test_special_likes_count(self):
        self.assertEqual(self.article.special_likes_count, 1)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=fake.first_name(),
            email=fake.email(),
            password=fake.password()
        )

        self.article = Article.objects.create(
            title='Test',
            content="test 123",
            user=self.user
        )

        self.comment = Comment.objects.create(
            body='This is a comment',
            user=self.user,
            article=self.article
        )

        self.upvote = CommentVote.objects.create(
            user=self.user,
            comment=self.comment
        )

        self.downvote = CommentVote.objects.create(
            downvote=True,
            user=self.user,
            comment=self.comment
        )

        CommentVote.objects.create(downvote=True, user=self.user, comment=self.comment)

    def test_create_comment(self):
        self.assertTrue(isinstance(self.comment, Comment))
        self.assertEqual(str(self.comment), f'{self.comment.body[:20]}...')
        self.assertEqual(self.article.comments_count, 1)

    def test_upvote_comment(self):
        upvotes_amount = self.comment.comment_votes.filter(downvote=False).count()
        self.assertEqual(upvotes_amount, 1)

    def test_downvote_comment(self):
        downvotes_amount = self.comment.comment_votes.filter(downvote=True).count()
        self.assertEqual(downvotes_amount, 2)

    def test_score_amount(self):
        self.assertEqual(self.comment.score, -1)
