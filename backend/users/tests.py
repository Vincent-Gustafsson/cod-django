from django.http import request
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate
from rest_framework.authtoken.models import Token

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


class AuthViewsTest(APITestCase):
    def test_create_user(self):
        # TODO This really shouldn't be hard-coded
        url = '/auth/register/'
        data = {
            'username': 'TestCreateUser',
            'email':'TestCreateUser@gmail.com',
            'password': '1234',
            'password2': '1234'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username=data['username']).username, data['username'])
    
    def test_login_user(self):
        url = '/auth/login/'

        user = User.objects.create_user(username='testLogin', email='testLogin@test.com', password='12345')

        response = self.client.post(url, {'username':'testLogin','password':'12345'}, format='json')

        token = Token.objects.get(user=user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['key'], token.key)

    def test_logout_user(self):
        user = User.objects.create_user(username='testUserLogout', email='testUserLogout@test.com', password='12345')
        token = Token.objects.create(user=user)

        response = self.client.post('/auth/logout/')
        force_authenticate(response, user=user, token=token)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_details(self):
        user = User.objects.create_user(username='testUserDetails', email='testUserDetails@test.com', password='12345')
        
        self.client.force_authenticate(user)
        response = self.client.get('/auth/user/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], user.id)
