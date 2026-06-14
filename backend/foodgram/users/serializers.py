from fields import Base64ImageField
from recipes.minified_serializer import RecipeMinifiedSerializer
from rest_framework import serializers

from .models import User


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя для чтения (GET/api/users/)."""

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
            'avatar',
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
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
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


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для проверки текущего пароля."""

    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate_current_password(self, value):
        """Проверяет текущий пароль."""
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