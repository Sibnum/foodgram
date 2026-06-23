"""API ViewSet'ы для приложения Foodgram.

Содержит ViewSet'ы для всех моделей проекта:
- TagViewSet (теги, read-only)
- IngredientViewSet (ингредиенты, read-only с фильтром по name)
- UserViewSet (пользователи: CRUD, подписки, аватар, пароль)
- RecipeViewSet (рецепты: CRUD, избранное, корзина, короткая ссылка)
"""

from django.http import HttpResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    SetAvatarSerializer,
    SetPasswordSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from ingredients.models import Ingredient
from recipes.models import Favorite, Recipe, ShoppingCart
from tags.models import Tag
from users.models import Subscription, User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Отображает запросы GET /api/tags/ и GET /api/tags/{id}/."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Обрабатывает GET /api/ingredients/ и GET /api/ingredients/{id}/."""

    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """Возвращает полный или фильтрованный по name queryset."""
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    """Представления пользователя.

    Описывает список, профиль, подписки, аватар, пароль.
    """

    queryset = User.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от выполняемого действия.

        Для действия 'create' выбирает CustomUserCreateSerializer,
        для остальных действий выбирает CustomUserSerializer.
        Возвращает сериализатор для текущего действия.
        """
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    def get_permissions(self):
        """Выбирает права доступа в зависимости от выполняемого действия.

        Для действия 'create' выбирает AllowAny, для действий 'me,
        subscriptions, subscribe, set_password, avatar' выбирает
        IsAuthenticated. Для всех остальных действий выбирает - AllowAny.
        """
        if self.action == 'create':
            self.permission_classes = (permissions.AllowAny,)
        elif self.action in (
            'me',
            'subscriptions',
            'subscribe',
            'set_password',
            'avatar',
        ):
            self.permission_classes = (permissions.IsAuthenticated,)
        else:
            self.permission_classes = (permissions.AllowAny,)
        return super().get_permissions()

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        """Возвращает пагинированный ответ со списком подписок пользователя."""
        authors = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context=self.get_serializer_context(),
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST'])
    def subscribe(self, request, id=None):
        """Создаёт подписку на автора."""
        author = self.get_object()
        if request.user == author:
            return Response(
                {'errors': 'Нельзя подписаться на себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        _, created = Subscription.objects.get_or_create(
            user=request.user, author=author
        )
        if not created:
            return Response(
                {'errors': 'Уже подписан.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SubscriptionSerializer(
            author,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def remove_subscribe(self, request, id=None):
        """Убирает подписку на автора."""
        author = self.get_object()
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author,
        ).first()
        if not subscription:
            return Response(
                {'errors': 'Подписка не найдена.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def me(self, request):
        """Возвращает профиль текущего пользователя."""
        serializer = CustomUserSerializer(
            request.user,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def set_password(self, request):
        """Выполняет валидацию и смену пароля."""
        serializer = SetPasswordSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['PUT'], url_path='me/avatar')
    def avatar(self, request):
        """Обновляет аватар пользователя."""
        serializer = SetAvatarSerializer(
            request.user, data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def remove_avatar(self, request):
        """Удаляет аватар."""
        request.user.avatar.delete()
        request.user.avatar = None
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Отображает рецепты: CRUD, избранное, корзину, короткую ссылку."""

    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбирает нужный сериализатор для текущего запроса."""
        if self.action in {'list', 'retrieve'}:
            return RecipeListSerializer
        return RecipeCreateSerializer

    def get_permissions(self):
        """Определяет набор разрешений для текущего запроса."""
        if self.action in {'create', }:
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.action in {'partial_update', 'update', 'destroy'}:
            self.permission_classes = (
                permissions.IsAuthenticated,
                IsAuthorOrReadOnly,
            )
        elif self.action in {
            'favorite',
            'shopping_cart',
            'download_shopping_cart',
        }:
            self.permission_classes = (permissions.IsAuthenticated,)
        else:
            self.permission_classes = (permissions.AllowAny,)
        return super().get_permissions()

    def get_response_serializer(self, instance):
        """Возвращает сериализованый ответ."""
        return RecipeListSerializer(
            instance, context=self.get_serializer_context()
        )

    def create(self, request, *args, **kwargs):
        """Создаёт рецепт и возвращает полное представление."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(author=self.request.user)
        response_serializer = self.get_response_serializer(instance)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Обновляет рецепт и возвращает полное представление."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = self.get_response_serializer(instance)
        return Response(response_serializer.data)

    @action(
        detail=True, methods=['POST'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавляет рецепт в избранное."""
        recipe = self.get_object()
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def remove_from_favorite(self, request, pk=None):
        """Удаляет рецепт из избранного."""
        recipe = self.get_object()
        favorite = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).first()
        if not favorite:
            return Response(
                {'errors': 'Рецепт отсутствует в избранном.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['POST'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет рецепт в список покупок."""
        recipe = self.get_object()
        serializer = ShoppingCartSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        """Удаляет рецепт из списка покупок."""
        recipe = self.get_object()
        cart_item = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).first()
        if not cart_item:
            return Response(
                {'errors': 'Рецепт отсутствует в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Генерирует короткую ссылку, если её ещё нет."""
        recipe = self.get_object()
        if not recipe.short_link:
            import secrets
            recipe.short_link = secrets.token_urlsafe(6)[:8]
            recipe.save(update_fields=['short_link'])
        full_url = f'https://{request.get_host()}/s/{recipe.short_link}/'
        return Response({'short-link': full_url})

    @action(
        detail=False, methods=['GET'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Скачивает файл со списком покупок."""
        cart_items = (
            ShoppingCart.objects
            .filter(user=request.user)
            .select_related('recipe')
        )
        ingredients = {}
        for item in cart_items:
            recipe_ingredients = item.recipe.ingredient_list.all()
            for ing in recipe_ingredients:
                name = ing.ingredient.name
                unit = ing.ingredient.measurement_unit
                key = f"{name} ({unit})"
                if key in ingredients:
                    ingredients[key] += ing.amount
                else:
                    ingredients[key] = ing.amount
        lines = ["Список покупок:"]
        for name, amount in ingredients.items():
            lines.append(f"{name} - {amount}")
        content = "\n".join(lines)
        return HttpResponse(content, content_type='text/plain; charset=utf-8')
