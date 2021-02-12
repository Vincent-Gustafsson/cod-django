from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

import faker

from ..models import Tag, Article, ArticleLike, Comment, CommentVote


fake = faker.Faker('en')
User = get_user_model()


class TagModelTest(TestCase):
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

        tag_names = ['javascript', 'python', 'vue', 'frontend', 'backend', 'docker']
        self.tags = []
        for name in tag_names:
            self.tags.append(Tag.objects.create(name=name))

    def test_create_tag(self):
        """ Creates tags. """
        self.assertEqual(Tag.objects.count(), 6)

    def test_maximum_tags_validation(self):
        """
        Articles can only have up to 5 tags.
        Raises an error when it goes over 5 tags.
        """
        # Adds 5 tags to the article
        for tag in self.tags[:5]:
            self.article.tags.add(tag)

        # Adds a 6th tag to the article which should trigger a Validation error.
        with self.assertRaises(ValidationError):
            self.article.tags.add(self.tags[5])


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

    def test_create_article(self):
        """ Creates an article. """
        self.assertTrue(isinstance(self.article, Article))
        self.assertEqual(str(self.article), f'{self.article.title[:10]}...')

    def test_likes_count(self):
        """ Returns the total amount of likes on the article. """
        self.assertEqual(self.article.likes_count, 1)

    def test_special_likes_count(self):
        """ Returns the total amount of special likes on the article. """
        self.assertEqual(self.article.special_likes_count, 1)

    def test_manager_only_fetches_non_drafts(self):
        """ Only returns article that's not drafts. """
        self.article_draft = Article.objects.create(
            title='Test',
            content="test 123",
            user=self.user,
            draft=True
        )

        self.assertEqual(Article.objects.count(), 1)

    def test_manager_only_fetches_drafts(self):
        """ Only returns article that's drafts. """
        self.article_draft = Article.objects.create(
            title='Test',
            content="test 123",
            user=self.user,
            draft=True
        )

        self.assertEqual(Article.drafts.count(), 1)


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
        """ Creates a comment. """
        self.assertTrue(isinstance(self.comment, Comment))
        self.assertEqual(str(self.comment), f'{self.comment.body[:20]}...')
        self.assertEqual(self.article.comments_count, 1)

    def test_upvote_comment(self):
        """ Upvotes a comment. """
        upvotes_amount = self.comment.comment_votes.filter(downvote=False).count()
        self.assertEqual(upvotes_amount, 1)

    def test_downvote_comment(self):
        """ Downvotes a comment. """
        downvotes_amount = self.comment.comment_votes.filter(downvote=True).count()
        self.assertEqual(downvotes_amount, 2)

    def test_score_amount(self):
        """ Returns the total score of a comment (upvotes - downvotes). """
        self.assertEqual(self.comment.score, -1)
