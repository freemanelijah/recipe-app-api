"""
Serializer for the user API view.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _
from rest_framework import serializers

# serializer.ModelSerializer base class. Serializers way to convert
# to and from python objects. They take json input that's posted
# from the API. Validates the input to make sure it's correct and then
# converts to a python object or a model in the database.
# Different base classes. serializer.Serializer vs serializer.ModelSerializer.
# Allow us to validate and save things automatically to a model that we define
# in our serializer. This is the class Meta.
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user objects."""

    class Meta:
        # Needs to know what model to represent
        model = get_user_model()
        # Needs to get created and/set when the model gets created. Only allow fields here
        # that the user is allowed to change through the API.
        fields = ['email', 'password', 'name']
        # Extras -> provides extra meta-data. Allows us to create constraints on the fields.
        # This is where we specify the rules for validating data.
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # Override create method. Called after validation and only after validation was successful.
    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        # create_user is a function we defined in our model manager.
        return get_user_model().objects.create_user(**validated_data)

    # Next step -> create a view that uses the serializer.

    # Overriding the update method on the user serializer. Update method is called whenever
    # we are performing update actions on the model that the serializer represents.
    # instance -> the instance that is being updated. The model instance.
    # validated_data -> data that has already passed through the serializer validation (email, password).
    def update(self, instance, validated_data):
        """Update and return user."""
        # Remove password from validated_data dictionary.
        # If no password, then default to None.
        password = validated_data.pop('password', None)
        # Calls update on ModelSerializer base class. Leveraging existing logic.
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """ Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},  # This makes the password field text hidden during input.
        trim_whitespace=False,
    )

    # Called on the serializer during the validation stage when it goes to validate the input to the
    # serializer. attrs -> attributes.
    def validate(self, attrs):
        """Validate and authenticate the user. """
        email = attrs.get('email')
        password = attrs.get('password')
        # authenticate is a built-in django function. request contains header messages. Checks that
        # email and password is correct. If correct, then the user is returned.
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            # Standard way to raise errors with serializers. If error is raised, then the view will
            # translate error into HTTP bad request error back to the client.
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

