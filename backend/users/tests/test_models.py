from django.test import TestCase

from ..models import User


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
