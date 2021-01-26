from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
import faker

from .models import Article, ArticleLike, Comment, CommentVote
from .serializers import ArticleSerializer


fake = faker.Faker()
User = get_user_model()


class ArticleViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=fake.first_name(),
            email=fake.email(),
            password=fake.password()
        )

        self.user_2 = User.objects.create_user(
            username=fake.first_name(),
            email=fake.email(),
            password=fake.password()
        )

        self.article = Article.objects.create(
            title='Test title',
            content='This is the content',
            user=self.user
        )

    def test_create_article_authorized(self):
        url = reverse('article-list')

        data = {
            'title': 'Test title',
            'content': 'This is the content'
        }

        self.client.force_authenticate(self.user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 2)
        self.assertEqual(Article.objects.get(pk=2).user, self.user)

    def test_create_article_unauthorized(self):
        url = reverse('article-list')

        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_articles(self):
        url = reverse('article-list')

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail_article(self):
        url = reverse('article-detail', kwargs={'pk': self.article.id})

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_own_article(self):
        url = reverse('article-detail', kwargs={'pk': self.article.id})

        data = {
            'title': 'Test title, updated',
            'content': 'This is the NEW content'
        }

        self.client.force_authenticate(self.user)
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Article.objects.get(pk=self.article.id).title, data['title'])
        self.assertEqual(Article.objects.get(pk=self.article.id).content, data['content'])

    def test_update_other_article(self):
        url = reverse('article-detail', kwargs={'pk': self.article.id})

        data = {
            'title': 'Test title, updated',
            'content': 'This is the NEW content'
        }

        self.client.force_authenticate(self.user_2)
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_article(self):
        url = reverse('article-detail', kwargs={'pk': self.article.id})

        self.client.force_authenticate(self.user)
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_article(self):
        url = reverse('article-detail', kwargs={'pk': self.article.id})

        self.client.force_authenticate(self.user_2)
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=fake.first_name(),
            email=fake.email(),
            password=fake.password()
        )

        self.user_2 = User.objects.create_user(
            username=fake.first_name(),
            email=fake.email(),
            password=fake.password()
        )

        self.article = Article.objects.create(
            title='Test title',
            content='This is the content',
            user=self.user
        )

        self.comment = Comment(
            body='TestComment',
            article=self.article,
            user=self.user
        )

    def test_create_comment_authorized(self):
        url = reverse('comment-list')

        data = {
            'body': 'Test Comment',
            'article': self.article.id
        }

        self.client.force_authenticate(self.user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.article.comments.count(), 1)
        self.assertEqual(self.article.comments.get().body, 'Test Comment')

    def test_create_comment_unauthorized(self):
        url = reverse('comment-list')

        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Perhaps this should be bundled with the Article tests.
    def test_list_article_comments(self):
        url = reverse('article-detail', kwargs={'pk': self.article.id})

        for _ in range(2):
            Comment.objects.create(
                body='TestComment',
                article=self.article,
                user=self.user
            )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), ArticleSerializer(self.article).data)

    def test_delete_own_comment(self):
        self.comment.save()
        url = reverse('comment-detail', kwargs={'pk': self.comment.id})

        self.client.force_authenticate(self.user)
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_comment(self):
        self.comment.save()
        url = reverse('comment-detail', kwargs={'pk': self.comment.id})

        self.client.force_authenticate(self.user_2)
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
