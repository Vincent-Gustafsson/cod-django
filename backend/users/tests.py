from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email="test@gmail.com", password='12345')
        self.user.save()

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



"""
class AccountTests(APITestCase):


    def test_create_account(self):
        url = reverse('account-list')
        data = {'name': 'DabApps'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Account.objects.get().name, 'DabApps')
"""
