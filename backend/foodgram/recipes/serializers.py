from rest_framework import serializers
from .models import (
    Favorite, Ingredient, IngredientInRecipes, Recipe, ShoppingCart, Tag
)
from .minified_serializer import RecipeMinifiedSerializer
from tags.serializers import TagSerializer
from users.serializers import CustomUserSerializer
from fields import Base64ImageField


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


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов и рецептов пользователя.

    Используется для запросов GET /api/recipes/ и GET /api/recipes/{id}/.
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

    def get_is_favorited(self, obj):
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
        validated_data.pop('author', None)
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


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов из избранного.

    Для POST/DELETE /api/recipes/{id}/favorite/.
    """

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        """Проверяет рецепт в избранном."""
        if Favorite.objects.filter(
            user=data['user'],
            recipe=data['recipe'],
        ).exists():
            raise serializers.ValidationError('Рецепт уже в избранном.')
        return data

    def to_representation(self, instance):
        """Возвращает мини-рецепт."""
        return RecipeMinifiedSerializer(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок.

    Для POST/DELETE /api/recipes/{id}/shopping_cart/
    """

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        """Проверяет наличие рецепта в списке покупок."""
        if ShoppingCart.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError('Рецепт уже в списке покупок.')
        return data

    def to_representation(self, instance):
        """Возвращает список покупок."""
        return RecipeMinifiedSerializer(instance.recipe).data
