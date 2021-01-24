from django.http import request
from django.test import TestCase
from django.urls import reverse
from django.urls.base import resolve

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate
from rest_framework.authtoken.models import Token

import faker

from .models import User
from .views import UserListRetrieveViewSet


fake = faker.Faker()


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


class UserRegistrationViewTest(APITestCase):
    def setUp(self):
        # Other user for unique validation
        self.non_unique_username = fake.first_name()
        self.non_unique_email = fake.email()
        User.objects.create_user(
            username=self.non_unique_username,
            email=self.non_unique_email,
            password=fake.password()
        )

        # Not unique user generation
        password = fake.password()
        self.non_unique_user = {
            'username': self.non_unique_username,
            'email': self.non_unique_email,
            'password': password,
            'password2': password
        }

        # Valid user generation
        valid_user_password = fake.password()
        self.valid_user = {
            'username': fake.first_name(),
            'email': fake.email(),
            'password': valid_user_password,
            'password2': valid_user_password
        }

        # Short password user generation
        short_user_password = fake.password()[:5]
        self.short_password_user = {
            'username': fake.first_name(),
            'email': fake.email(),
            'password': short_user_password,
            'password2': short_user_password
        }

        # Non matching passwords user generation
        self.non_matching_passwords_user = {
            'username': fake.first_name(),
            'email': fake.email(),
            'password': fake.password()[:6],
            'password2': fake.password()[:6]
        }

    def test_create_valid_user(self):
        """ Tests if user registration works. """
        url = reverse('rest_register')

        response = self.client.post(url, self.valid_user, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.last().username, self.valid_user['username'])
        self.assertEqual(response.data['key'], Token.objects.get().key)

    def test_password_validation_length(self):
        """ Tests if the password length validation works. """
        url = reverse('rest_register')

        response = self.client.post(url, self.short_password_user, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('The password must be at least 6 characters long.' in response.json()['password'])

    def test_password_validation_must_match(self):
        """ Tests if the password matching validation works. """
        url = reverse('rest_register')

        response = self.client.post(url, self.non_matching_passwords_user, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['password'], 'Passwords must match.')

    def test_unique_constraints(self):
        """ Tests if the unique constraints on username and email works. """
        url = reverse('rest_register')

        response = self.client.post(url, self.non_unique_user, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['username'][0], 'user with this username already exists.')
        self.assertEqual(response.json()['email'][0], 'user with this email already exists.')


class AuthViewsTest(APITestCase):
    def test_login_user(self):
        url = reverse('rest_login')

        user = User.objects.create_user(username='testLogin', email='testLogin@test.com', password='12345')

        response = self.client.post(url, {'username':'testLogin','password':'12345'}, format='json')

        token = Token.objects.get(user=user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['key'], token.key)

    def test_logout_user(self):
        url = reverse('rest_logout')

        user = User.objects.create_user(username='testUserLogout', email='testUserLogout@test.com', password='12345')
        token = Token.objects.create(user=user)

        response = self.client.post(url)
        force_authenticate(response, user=user, token=token)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_details(self):
        url = reverse('rest_user_details')

        user = User.objects.create_user(username='testUserDetails', email='testUserDetails@test.com', password='12345')
        
        self.client.force_authenticate(user)
        response = self.client.get('/auth/user/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], user.id)


class UserViewSetTest(APITestCase):
    def setUp(self):
        for i in range(10):
            User.objects.create_user(
                username= f'{i}{fake.first_name()}',
                email=f'{i}{fake.email()}',
                password=fake.password()
            )

        self.users = User.objects.all()

    def test_list_users(self):
        """ Tests if the user-list endpoint returns all the users """
        # TODO Will have to add test cases for search params and stuff
        url = reverse('user-list')
        
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), User.objects.count())

        for (i, user) in enumerate(self.users):
            self.assertEqual(user.username, response.json()[i]['username'])
    
    def test_retrieve_user(self):
        """ Tests if the user detail endpoint returns the right user """
        url = reverse('user-detail', kwargs={'pk': self.users[0].id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], self.users[0].username)
