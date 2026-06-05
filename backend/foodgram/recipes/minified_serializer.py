from rest_framework import serializers
from .models import Recipe


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода укороченной версии рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
