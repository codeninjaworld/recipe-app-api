""" Test tags APIs """
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import (
    Tag,
    Recipe,
)
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    """ Return a tag details matching the ID """
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='test@example.com', password='test121'):
    """ Create and return a user """
    return get_user_model().objects.create_user(email, password)

class PublicTagsAPITests(TestCase):
    """ Tests for unauthenticated API requests """

    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """ Tests auth us required to retrieve Tags """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)\

class PrivateTagsAPITests(TestCase):
    """ Test authenticated API requests """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
    
    def test_retrieve_tags(self):
        """ Test for retrieving tags """
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Test retrieve tags limited to the authenticated user """
        user2 = create_user(email='test2@example.com', password='test1212')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Delicious')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """ Test updating a tag """
        tag = Tag.objects.create(user=self.user, name='swadistht')

        payload = {'name': 'Swadist'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """ Test delete a tag  feature """
        tag = Tag.objects.create(user=self.user, name="Breakfast")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
    
    def test_filtering_tags_assigned_to_recipes(self):
        """ Test filter the tags assigned to Recipes """
        tag1 = Tag.objects.create(user=self.user, name='vegan')
        tag2 = Tag.objects.create(user=self.user, name='vegetarion')

        recipe = Recipe.objects.create(
            title='Toast',
            price=Decimal('6.5'),
            time_minutes=80,
            user=self.user
        )

        recipe.tags.add(tag1)

        res= self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_are_unique(self):
        """ Test filtered tags are unique"""
        tag = Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='vegetarion')

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Bread toast',
            price=Decimal('23.1'),
            time_minutes=10
        )

        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Bread jam',
            price=Decimal('22.1'),
            time_minutes=5
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
