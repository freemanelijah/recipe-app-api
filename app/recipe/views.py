"""
Views for the recipe APIs.
"""
from rest_framework import (
    viewsets,
    mixins,  # Add to a view to add additional functionality.
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe import serializers


# ModelViewSet is set up to work directly with a model. Viewset will
# create multiple endpoints, list, detail, etc. When calling the detail
# endpoint, need to have the ViewSet call the RecipeDetailSerializer. Override
# the method get_serializer_class(self). (list-view endpoint is default).
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    # Make the RecipeDetailSerializer the default serializer.
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()  # Represents all objects available to this view.
    authentication_classes = [TokenAuthentication]  # Need to be authenticated to reach API.
    permission_classes = [IsAuthenticated]  # Need to have permissions.

    # Override get_queryset method.
    def get_queryset(self):
        """Retrieve recipes for authenticated users."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            # If we make an HTTP GET request to the root of the API, then
            # we'll get the list. Returning a reference to the class by not adding
            # (). Django will instantiate the class using the reference.
            return serializers.RecipeSerializer
        return self.serializer_class

    # Override behaviour for when Django rest frameworks saves a model in a viewset.
    # Look for other methods to override in DRF. serializer -> validated_data.
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

# Base of other ViewSets. RecipeAttr -> tags and ingredients are attributes assigned
# to a recipe.
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')

class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in teh database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()


# Refactor TagViewSet and IngredientViewSet. Lots of duplicate code and similar
# functionality.
# ----------------------------------------------------------------------------

# GenericViewSet allows you to use mixins. In order to update the tag, we
# want to use the update model mixin.
#class TagViewSet(mixins.DestroyModelMixin,
#                 mixins.UpdateModelMixin,
#                 mixins.ListModelMixin,
#                 viewsets.GenericViewSet):
#    """Manage tags in the database."""
#    serializer_class = serializers.TagSerializer
#    queryset = Tag.objects.all()
#    authentication_classes = [TokenAuthentication]
#    permission_classes = [IsAuthenticated]
#
#    # Override get_queryset method that comes with the viewset to return objects
#    # for the authenticated user. Without, default function will return all tags
#    # in the db.
#    def get_queryset(self):
#        """Filter queryset to authenticated user."""
#        return self.queryset.filter(user=self.request.user).order_by('-name')
#
#class IngredientViewSet(mixins.DestroyModelMixin,
#                        mixins.UpdateModelMixin,
#                        mixins.ListModelMixin,
#                        viewsets.GenericViewSet):
#    """Manage ingredients in the database."""
#    serializer_class = serializers.IngredientSerializer
#    queryset = Ingredient.objects.all()
#    authentication_classes = [TokenAuthentication]
#    permission_classes = [IsAuthenticated]  # All users must be authenticated when using API.
#
#    def get_queryset(self):
#        """Filter queryset to authenticated user."""
#        return self.queryset.filter(user=self.request.user).order_by('-name')