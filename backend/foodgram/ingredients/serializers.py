from rest_framework import serializers

from .models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов (GET /api/ingredients/)"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
