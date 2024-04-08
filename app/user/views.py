"""
Views for the user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)

# Generics -> handles requests in default way, with some overriding allowed.
# CreateAPIView handles an http post request that's used for creating objects.
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    # We know what model we want to create because the UserSerializer has it defined.
    serializer_class = UserSerializer
    # Next step -> connect to a URL.


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    # define custom serializer class. ObtainAuthToken uses the username and password as default
    # instead of email and password.
    serializer_class = AuthTokenSerializer
    # Uses default renderer class for ObtainAuthToken view. If we didn't use this, we wouldn't get the
    # browsable api that's used for the django rest framework. Enable it.
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# RetrieveUpdateAPIView - provided by Django for retrieving HTTP GET and updating HTTP PUT/PATCH
# objects in the database.
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    # Django rest framework.
    authentication_classes = [authentication.TokenAuthentication]
    # We know who the user is. What is that user allowed to do in the system?
    permission_classes = [permissions.IsAuthenticated]

    # Override get object. Gets the object for any HTTP GET request. WHen user is authenticated
    # the authenticated user is assigned to the request object in the view.
    # When a HTTP GET request is made to the endpoint, it is going to call get_object which is going
    # to retrieve the user. Run through the serializer and then return the result to the API.
    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
