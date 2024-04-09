"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

# Default router provided by django rest framework. Use with API view,
# to automatically create routes for all the different options available
# for that view.
from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
# Register our view with the router. Recipe is going to have auto generated endpoints.
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

# Used for reverse lookup
app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
