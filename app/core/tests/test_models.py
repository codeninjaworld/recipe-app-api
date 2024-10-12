"""
    Test Models test cases
"""
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def create_user(email='test@example.com', password='test122'):
    """ create and return test user """
    return get_user_model().objects.create_user(email, password)


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

    def test_create_recipe(self):
        """ Test creating recipe is successful """
        user = get_user_model().objects.create_user(
            'test@example.com',
            'Test@d131'
        )

        recipe = models.Recipe.objects.create(
            user = user,
            title='Sample recipe',
            time_minutes =5,
            price=Decimal('5.50'),
            description='Sample recipe description'
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """ Test creation of tag is successful """
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """ Test creating an ingredient is successful """
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient'
        )

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """ Test generating image patch """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
