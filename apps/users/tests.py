from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123',
            role='customer'
        )
        self.forgot_password_url = reverse('forgot_password')
        self.reset_password_url = reverse('reset_password')

    def test_forgot_password_success(self):
        response = self.client.post(self.forgot_password_url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset Request', mail.outbox[0].subject)
        self.assertIn('test@example.com', mail.outbox[0].to)

    def test_forgot_password_invalid_email(self):
        response = self.client.post(self.forgot_password_url, {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_password_success(self):
        # First get the token and uidb64
        token = default_token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))

        data = {
            'uidb64': uidb64,
            'token': token,
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_reset_password_invalid_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        data = {
            'uidb64': uidb64,
            'token': 'invalid-token',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.check_password('newpassword123'))

    def test_reset_password_mismatch(self):
        token = default_token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        data = {
            'uidb64': uidb64,
            'token': token,
            'password': 'newpassword123',
            'confirm_password': 'mismatchpassword'
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
