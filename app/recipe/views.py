"""
Views for the recipe APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
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
