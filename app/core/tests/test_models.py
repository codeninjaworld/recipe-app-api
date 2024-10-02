"""
    Test Models test cases
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    """ Test models """

    def test_create_user_with_email_address_successful(self):
        """ Test creating user model comparing it against """
        email = "email@example.com"
        password= "password123"

        user = get_user_model().objects.create_user(
            email= email,
            password= password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """ Test that creating user without an email raises error """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample122')

    def test_create_superuser(self):
        """ Test creating super user """
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'sampleq1'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)