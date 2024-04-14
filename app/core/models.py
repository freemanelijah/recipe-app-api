"""
Database models.
"""

import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

# Used to generate the path to the image that we upload.
# instance -> the instance that of the object that the image is being uploaded too.
def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1] # stripping off the extension.
    # uuid() -> calling the function. Creating a new filename using uuid and append
    # the previous extension. (e.g. cat.jpg -> 3o4u2428234.jpg)
    filename = f'{uuid.uuid4()}{ext}'

    # use instead hardcoding the string. Ensures that string will
    # be created in the correct format for the OS that the code is
    # being executed on.
    return os.path.join('uploads', 'recipe', filename)



class UserManager(BaseUserManager):
    """ Manager for user model. """

    def create_user(self, email, password=None, **extra_fields):
        """Create, save, and return a new user."""
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)  # set the password and encrypts it before saving the db.
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create, save, and return a new superuser. """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


# AbstractBaseUser -> contains auth system but includes no fields.
# PermissionsMixin -> contains permissions functionality and related fields.
class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Assign user manager to custom user class.
    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # We defined this in the settings.py file. Could specify as a string.
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    # Possible to have many different recipes that have many different tags. Any recipe
    # can be associated to any tag and vice versa.
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    # image can be null, pass in a reference to the function that generates the path to image.
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title

class Tag(models.Model):
    """Tag for filtering recipes.."""
    name = models.CharField(max_length=255)
    # Link tag to authorized user.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredients for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
