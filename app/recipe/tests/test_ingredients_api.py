""" Tests for Ingredients """
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Ingredient,
    Recipe,
)
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def create_user(email='test@example.com', password='tets121'):
    """ create and return user """
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(ingredient_id):
    """ Get the Ingredient details """
    return reverse('recipe:ingredient-detail', args=[ingredient_id])

class PublicIngredientApiTests(TestCase):
    """ Test retriveing Ingredients by unauthenticated users """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test auth required for retrieving ingredients """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
class PrivateIngredientApiTests(TestCase):
    """ Test authenticated API requests """

    def setUp(self):
        self.client=APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """ Test retrieving a list of ingredients """
        Ingredient.objects.create(user=self.user, name='Vanilla')
        Ingredient.objects.create(user=self.user, name='Raisin')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer= IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Test retrieving ingredients created by user themselves """
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Elaichi')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """ Test upgdating an ingredient """
        ingredient = Ingredient.objects.create(user=self.user, name='cashew')

        payload = {'name': 'dates'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()

        self.assertEqual(ingredient.name, payload['name'])
    
    def test_delete_ingredient(self):
        """ Test deleting an ingredient """
        ingredient = Ingredient.objects.create(user=self.user, name='lettuce')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())
    
    def test_filter_ingredients_assigned_to_recipes(self):
        """ Test listing ingredients assinged to recipes """
        in1 = Ingredient.objects.create(user=self.user, name='Pepper')
        in2 = Ingredient.objects.create(user=self.user, name='Ginger')

        recipe = Recipe.objects.create(
            user=self.user,
            title='Indian dish',
            price=Decimal('5.50'),
            time_minutes=10
        )

        recipe.ingredients.add(in1)

        res=self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        
        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """ Test filtered ingredeints return the unique list """
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Egg Benedict',
            time_minutes= 15,
            price=Decimal('4.5')
        )

        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Herb Eggs',
            time_minutes=20,
            price=Decimal('55.1')
        )

        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res=self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
    
