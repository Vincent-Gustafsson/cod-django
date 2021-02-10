from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from users.models import UserFollowing

from ..models import Tag, Article


User = get_user_model()


class FeedViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='User1',
            email='user1@gmail.com',
            password='12345'
        )

        self.user_2 = User.objects.create_user(
            username='User2',
            email='user2@gmail.com',
            password='12345'
        )

        self.javascript_tag = Tag.objects.create(name='Javascript')

        self.python_tag = Tag.objects.create(name='Python')

        for _ in range(3):
            Article.objects.create(
                title='article',
                content='a',
                user=self.user
            )

        for _ in range(3):
            article = Article.objects.create(
                title='article',
                content='a',
                user=self.user_2
            )

            article.tags.add(self.javascript_tag, self.python_tag)

        self.javascript_tag.followers.add(self.user)
        self.python_tag.followers.add(self.user_2)

        UserFollowing.objects.create(user_follows=self.user, user_followed=self.user_2)
        UserFollowing.objects.create(user_follows=self.user_2, user_followed=self.user)

    def test_list_anonymous_feed(self):
        """
        Lists the latest articles paginated because the user is not authenticated.
        """
        url = reverse('article-feed')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json()['results'][0]), Article.objects.count())

    def test_list_user_feed(self):
        """
        Lists the feed for "self.user". This feed excludes the user's own articles,
        lists all the users and tags that the user is following.
        """
        url = reverse('article-feed')

        self.client.force_authenticate(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json()['results'][0]['followed_tags']), 1)

        self.assertEqual(len(response.json()['results'][1]), 1)

        self.assertEqual(
            len(response.json()['results'][2]),
            Article.objects.exclude(user=self.user).count()
        )

    def test_list_user_2_feed(self):
        """
        Lists the feed for "self.user_2". This feed excludes the user's own articles,
        lists all the users and tags that the user is following.
        """
        url = reverse('article-feed')

        self.client.force_authenticate(self.user_2)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json()['results'][0]['followed_tags']), 1)

        self.assertEqual(len(response.json()['results'][1]), 1)

        self.assertEqual(
            len(response.json()['results'][2]),
            Article.objects.exclude(user=self.user_2).count()
        )
