"""
Views for the recipe APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


# ModelViewSet is set up to work directly with a model. Viewset will
# create multiple endpoints, list, detail, etc.
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()  # Represents all objects available to this view.
    authentication_classes = [TokenAuthentication]  # Need to be authenticated to reach API.
    permission_classes = [IsAuthenticated]  # Need to have permissions.

    # Override get_queryset method.
    def get_queryset(self):
        """Retrieve recipes for authenticated users."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
