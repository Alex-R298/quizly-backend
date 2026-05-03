from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


class RegisterUserTestCase(APITestCase):
    def test_register_user(self):
        response = self.client.post('/api/register/', data={
            "username": "your_username",
            "password": "your_password",
            "confirmed_password": "your_password",
            "email": "your_email@example.com"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"detail": "User created successfully!"})

    def test_register_password_mismatch(self):
        response = self.client.post('/api/register/', data={
            "username": "your_username",
            "password": "your_password",
            "confirmed_password": "different_password",
            "email": "your_email@example.com"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        response1 = self.client.post('/api/register/', data={
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "confirmed_password": "examplePassword",
        }, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post('/api/register/', data={
            "username": "exampleUsername",
            "email": "another@mail.de",
            "password": "examplePassword",
            "confirmed_password": "examplePassword",
        }, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_email(self):
        response = self.client.post('/api/register/', data={
            "username": "exampleUsername",
            "password": "examplePassword",
            "confirmed_password": "examplePassword"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_username(self):
        response = self.client.post('/api/register/', data={
            "email": "example@mail.de",
            "password": "examplePassword",
            "confirmed_password": "examplePassword",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email(self):
        response = self.client.post('/api/register/', data={
            "username": "exampleUsername",
            "email": "not-an-email",
            "password": "examplePassword",
            "confirmed_password": "examplePassword",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginUserTestCase(APITestCase):
    def setUp(self):
        self.username = "exampleUsername"
        self.password = "examplePassword"
        self.email = "example@mail.de"
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
        )

    def test_login_success(self):
        response = self.client.post('/api/login/', data={
            "username": self.username,
            "password": self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("detail"), "Login successfully!")
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], self.username)
        self.assertEqual(response.data["user"]["email"], self.email)
        self.assertEqual(response.data["user"]["id"], self.user.id)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_login_invalid_password(self):
        response = self.client.post('/api/login/', data={
            "username": self.username,
            "password": "wrongPassword",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unknown_user(self):
        response = self.client.post('/api/login/', data={
            "username": "doesNotExist",
            "password": "somePassword",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        response = self.client.post('/api/login/', data={
            "username": self.username,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutUserTestCase(APITestCase):
    def setUp(self):
        self.username = "exampleUsername"
        self.password = "examplePassword"
        self.user = User.objects.create_user(
            username=self.username,
            email="example@mail.de",
            password=self.password,
        )

    def _login(self):
        return self.client.post('/api/login/', data={
            "username": self.username,
            "password": self.password,
        }, format='json')

    def test_logout_success(self):
        self._login()
        response = self.client.post('/api/logout/', data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("detail"),
            "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
        )

    def test_logout_unauthenticated(self):
        response = self.client.post('/api/logout/', data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTestCase(APITestCase):
    def setUp(self):
        self.username = "exampleUsername"
        self.password = "examplePassword"
        self.user = User.objects.create_user(
            username=self.username,
            email="example@mail.de",
            password=self.password,
        )

    def _login(self):
        return self.client.post('/api/login/', data={
            "username": self.username,
            "password": self.password,
        }, format='json')

    def test_token_refresh_success(self):
        self._login()
        response = self.client.post('/api/token/refresh/', data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("detail"), "Token refreshed")
        self.assertIn("access_token", response.cookies)

    def test_token_refresh_missing_cookie(self):
        response = self.client.post('/api/token/refresh/', data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)




