from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import UserFollowing

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email="test@gmail.com",
            password='12345'
        )

    def test_create_user(self):
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(str(self.user), self.user.username)

    def test_user_default_display_name(self):
        self.assertEqual(self.user.display_name, self.user.username)

    def test_user_change_display_name(self):
        self.user.display_name = 'another_name'
        self.user.save()
        self.assertNotEqual(self.user.display_name, self.user.username)

    def test_user_avatar_change_to_none(self):
        """
            If the user "resets" their avatar they set it to None / null.
            This test ensures that the avatar image is set to the default
            image if the value of avatar is None.
        """
        self.user.avatar = None
        self.user.save()


class UserFollowingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email="test@gmail.com",
            password='12345'
        )

        self.user_2 = User.objects.create_user(
            username='testuser_2',
            email="test_2@gmail.com",
            password='12345'
        )

    def test_follow_user(self):
        following = UserFollowing.objects.create(
            user_follows=self.user,
            user_followed=self.user_2
        )

        self.assertEqual(str(following), 'testuser follows testuser_2')
        self.assertEqual(self.user.following.get().user_followed, self.user_2)

        self.assertEqual(self.user_2.followers.get().user_follows, self.user)
        self.assertEqual(self.user_2.followers.count(), 1)
