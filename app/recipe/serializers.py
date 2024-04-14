"""Serializers for recipe APIs"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    # many=True, we could have a list of tags.
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingredients',
        ]
        read_only_fields = ['id']  # Don't want to allow changing of the id in the DB.

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        # Get the authenticated user. Looks different here because we are getting
        # the authenticated user in the serializer instead of the view. Context is
        # passed to the serializer by the view when using the serializer for that view.
        auth_user = self.context['request'].user
        # get_or_create -> helper function provided by model manager. Gets value if
        # exists or creates the tag if it does not exist in the db.
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag, # Alternative; name=tag['name'], **tag, take all values in tag.
                # Future-proof if new fields get added to tag.
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, create = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)


    # Custom logic for creating recipes.
    def create(self, validated_data):
        """Creating a recipe."""
        # If tags doesn't exist in validated_data, default to an empty list. Use pop to make sure
        # we remove the tags before we create the recipe.
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        # Remove the tags leaving only the recipe. Create the recipe.
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    # instance -> this is the instance of the recipe we are retrieving.
    # TypeError: Direct assignment to forward side of a many-to-many prohibited.
    # Use ingredients.set() instead. Error was thrown because we are not popping
    # the ingredients from the validated_data.
    def update(self, instance, validated_data):
        """Update recipe"""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            # Clear all tags assigned to the recipe.
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        # If ingredients is not None, then there is a value associated. Clear all
        # ingredients and then assign new ingredients from validated_data.
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        # Everything in validated_data except for tags.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        # The description is an additional field.
        fields = RecipeSerializer.Meta.fields + ['description', 'image']

class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}

