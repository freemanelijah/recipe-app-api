"""
Views for the recipe APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,  # Add to a view to add additional functionality.
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
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
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    # Make the RecipeDetailSerializer the default serializer.
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()  # Represents all objects available to this view.
    authentication_classes = [TokenAuthentication]  # Need to be authenticated to reach API.
    permission_classes = [IsAuthenticated]  # Need to have permissions.

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers"""
        # Splitting a command seperated string, e.g. "1,2,3"
        # Once split, we can use them for filtering.
        return [int(str_id) for str_id in qs.split(',')]

    # Override get_queryset method.
    def get_queryset(self):
        """Retrieve recipes for authenticated users."""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids) # Filter on related fields in a DB using django.
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user).order_by('-id').distinct()

        # Instead of returning the self queryset, instead return the one we are building.
        #return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            # If we make an HTTP GET request to the root of the API, then
            # we'll get the list. Returning a reference to the class by not adding
            # (). Django will instantiate the class using the reference.
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            # custom action defined as a different method in recipe view set. Actions
            # are ways we can add additional functionality on top of default view set functionality.
            return serializers.RecipeImageSerializer

        return self.serializer_class

    # Override behaviour for when Django rest frameworks saves a model in a viewset.
    # Look for other methods to override in DRF. serializer -> validated_data.
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    # Define custom action to provide addtional functionality on top of the
    # existing API. detail=True, action will apply to detail endpoint of model
    # view set. A specific recipe-id is provided.
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        recipe = self.get_object() # Get's the recipe object using the PK.
        # Returns the image serializer as specified in the above get_serializer_class
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()  # Save image to the db.
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Assume serializer was not valid so return errors.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Base of other ViewSets. RecipeAttr -> tags and ingredients are attributes assigned
# to a recipe.
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1], # Allowed to pass only 0 or 1 to assigned_only parameter
                description='Filter by items assigned to recipe.',
            )
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))  # 0 is default value that's returned
        )
        queryset = self.queryset
        if assigned_only:
            # There is a recipe associated with the value.
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user).order_by('-name').distinct()

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