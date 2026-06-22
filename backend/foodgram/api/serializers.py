"""Сериализаторы DRF для API приложения Foodgram.

Содержит все сериализаторы проекта:
- TagSerializer, IngredientSerializer
- CustomUserSerializer, CustomUserCreateSerializer
- SetPasswordSerializer, SetAvatarSerializer
- RecipeMinifiedSerializer, SubscriptionSerializer
- IngredientInRecipeSerializer, RecipeListSerializer, RecipeCreateSerializer
- FavoriteSerializer, ShoppingCartSerializer
"""

from rest_framework import serializers

from fields import Base64ImageField
from recipes.models import (
    Favorite, Ingredient, IngredientInRecipes, Recipe, ShoppingCart
)
from tags.models import Tag
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения тегов (GET /api/tags/)."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов (GET /api/ingredients/)."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя для чтения (GET /api/users/)."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar',
        )

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на этого.

        obj - объект User, который сейчас сериализуется.
        self.context.get('request') - текущий HTTP-запрос.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.subscriptions.filter(author=obj).exists()
        return False


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации (POST /api/users/)."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',
        )

    def create(self, validated_data):
        """Создаёт пользователя с хешированием пароля."""
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""

    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate_current_password(self, value):
        """Проверяет текущий пароль. Неверный пароль выбрасывает исключение."""
        request = self.context.get('request')
        if not request.user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль.')
        return value


class SetAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода укороченной версии рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя и его рецептов.

    Для GET /api/users/subscriptions/
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True,
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_is_subscribed(self, user):
        """Возвращает подписку, раз находится в этом списке."""
        return True

    def get_recipes(self, user):
        """Проверяет лимит для рецепта."""
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = user.recipes.all()
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except (ValueError, TypeError):
                pass
        return RecipeMinifiedSerializer(recipes, many=True).data


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиента в рецепте с количеством."""

    id = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='id',
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='name',
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='measurement_unit',
    )

    class Meta:
        model = IngredientInRecipes
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class IngredientInputSerializer(serializers.Serializer):
    """Сериализатор для одного ингредиента во входных данных рецепта."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f'Ингредиент с id={value} не найден.'
            )
        return value


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов и рецептов пользователя.

    Используется для запросов GET /api/recipes/ и GET /api/recipes/{id}/.
    """

    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = CustomUserSerializer(
        read_only=True
    )
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

    def get_is_favorited(self, recipe):
        """Возвращает список избранного, если пользователь аутентифицирован."""
        request = self.context.get('request')
        user_authenticated = request and request.user.is_authenticated
        return (
            user_authenticated
            and recipe.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        """Возвращает список покупок, если пользователь аутентифицирован."""
        request = self.context.get('request')
        user_authenticated = request and request.user.is_authenticated
        return (
            user_authenticated
            and recipe.shopping_cart.filter(user=request.user).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта.

    Используется для POST и PATCH /api/recipes/.
    """

    image = Base64ImageField()
    ingredients = IngredientInputSerializer(
        many=True,
        write_only=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
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
                'Нужно указать хотя бы один ингредиент.'
            )
        if not isinstance(value, list):
            type_value = type(value)
            raise serializers.ValidationError(
                f'Ожидался список ингредиентов, получен '
                f'{type_value.__name__}: {value}'
            )
        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                f'Ингредиенты не должны повторяться. '
                f'Получены id: {ingredient_ids}'
            )
        return value

    def validate_tags(self, value):
        """Валидирует теги."""
        if not value:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один тег.'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return value

    def validate(self, attrs):
        """Проверяет наличие обязательных полей даже при PATCH."""
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                {'ingredients': 'Обязательное поле.'}
            )
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                {'tags': 'Обязательное поле.'}
            )
        return attrs

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
        image_data = validated_data.pop('image', None)
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
        if image_data is not None:
            instance.image = image_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


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
            user=data['user'], recipe=data['recipe'],
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
            user=data['user'], recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError('Рецепт уже в списке покупок.')
        return data

    def to_representation(self, instance):
        """Возвращает список покупок."""
        return RecipeMinifiedSerializer(instance.recipe).data
