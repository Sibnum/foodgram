import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Ingredient, IngredientInRecipes, Recipe, Tag
from tags.serializers import TagSerializer
from users.serializers import CustomUserSerializer


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиента в рецепте с количеством."""

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода укороченной версии рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов и рецептов пользователя.

    Используется для запросов GET /api/recipes/ и GET /api/recipes/{id}/
    """

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredient_list'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorite(self, obj):
        """Возвращает список избранного, если пользователь аутентифицирован."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Возвращает список покупок, если пользователь аутентифицирован."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shopping_cart.filter(user=request.user).exists()
        return False


class Base64ImageField(serializers.ImageField):
    """Декодирует base64-строку в файл изображения."""

    def to_internal_value(self, data):
        """Декодирует base64-строку и возвращает файловый объект."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            name = f'{uuid.uuid4()}.{ext}'
            data = ContentFile(base64.b64decode(imgstr), name=name)
        return super().to_internal_value(data)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта.

    Используется для POST и PATCH /api/recipes/.
    """

    image = Base64ImageField()
    ingredients = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            allow_empty=False
        ),
        write_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        """Валидация списка ингредиентов."""
        if not value:
            raise serializers.ValidationError(
                "Нужно указать хотя бы один ингредиент."
            )
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    'Каждый ингредиент должен быть объектом {id, amount}'
                )
            if 'id' not in item or 'amount' not in item:
                raise serializers.ValidationError(
                    'У каждого ингредиента должны быть поля id и amount.'
                )
            if not Ingredient.objects.filter(id=item['id']).exists():
                raise serializers.ValidationError(
                    f'Ингредиент с id={item["id"]} не найден.'
                )
            if item['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть >= 1.'
                )
        return value

    def validate_tags(self, value):
        """Валидирует теги."""
        if not value:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один тег.'
            )
        return value

    def create(self, validated_data):
        """Создаёт рецепт."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        image_data = validated_data.pop('image')

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            image=image_data,
            **validated_data
        )
        recipe.tags.set(tags_data)

        bulk_ingredients = [
            IngredientInRecipes(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount']
            )
            for item in ingredients_data
        ]
        IngredientInRecipes.objects.bulk_create(bulk_ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        if ingredients_data is not None:
            instance.ingredient_list.all().delete()
            bulk_ingredients = [
                IngredientInRecipes(
                    recipe=instance,
                    ingredient_id=item['id'],
                    amount=item['amount']
                )
                for item in ingredients_data
            ]
            IngredientInRecipes.objects.bulk_create(bulk_ingredients)
        if tags_data is not None:
            instance.tags.set(tags_data)
        return super().update(instance, validated_data)
