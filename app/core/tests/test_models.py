"""
Test for models.
"""
from unittest.mock import patch  # tool to use to mock objects. Replace behaviour for purpose of testing.
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

# When testing models besides the user model, we'll want to test the model directly.
from core import models

# Helper function to create a new user.
def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """ Test models. """

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        # get_user_model() helper function provided by Django to get the default user_model.
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
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
        """Creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )
        # is_superuser is the field provided by the PermissionsMixins.
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        # Test user is going to be assigned to recipe.
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'), # Not best practice to use Decimal/Float for storing prices. Use integer instead.
            description='Sample recipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        # Create an instance of a tag object using the objects create method.
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient1',
        )
        self.assertEqual(str(ingredient), ingredient.name)

    # patch the uuid function that's imported into the models. Replace the
    # behaviour of UUID. We don't want to create a real one, so we mock
    # the behaviour.
    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        # recipe_image_file_path is used to generate the path to the image
        # that is being uploaded. None is used instead of the instance
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')

