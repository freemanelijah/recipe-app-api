"""
Tests for recipe apis
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import (
    RecipeSerializer,  # Provides recipe preview in the listing.
    RecipeDetailSerializer,  # Adds more fields and provides more details for recipes.
)

RECIPES_URL = reverse('recipe:recipe-list')


# Why declare a function rather than RECIPE_URL? Need to pass in the ID
# to the recipe id.
def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


# Helper function to be used in tests to help create a recipe.
# **params -> a dictionary that is passed to the create_recipe function.
def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    # Recipes can be retrieved only by authorized users.
    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        # Creating two recipes in the DB.
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        # Returned in order of the ID they are creating with.
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # res.data is the data from the response to the request
        # serializer.data is the data dictionary of the objects
        # passed through the serializer
        self.assertEqual(res.data, serializer.data)

def test_recipe_list_limited_to_user(self):
    """Test list of recipes is limited to authenticated user."""
    other_user = get_user_model().objects.create_user(
        'other@example.com',
        'password123',
    )
    create_recipe(user=other_user) # Our other user.
    create_recipe(user=self.user) # User who is authenticated.

    res = self.client.get(RECIPES_URL)

    # Testing to see only recipes created by the authenticated user.
    # Filtering by authenticated user.
    recipes = Recipe.objects.filter(user=self.user)
    serializer = RecipeSerializer(recipes, many=True)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

def test_get_recipe_detail(self):
    """Test get recipe detail."""
    recipe = create_recipe(user=self.user)

    url = detail_url(recipe.id)
    res = self.client.get(url)

    serializer = RecipeDetailSerializer(recipe)
    # Check the result from the client against the serializer.
    self.assertEqual(res.data, serializer.data)


