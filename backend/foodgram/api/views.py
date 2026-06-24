"""API ViewSet'ы для приложения Foodgram.

Содержит ViewSet'ы для всех моделей проекта:
- TagViewSet (теги, read-only)
- IngredientViewSet (ингредиенты, read-only с фильтром по name)
- UserViewSet (пользователи: CRUD, подписки, аватар, пароль)
- RecipeViewSet (рецепты: CRUD, избранное, корзина, короткая ссылка)
"""

import io
import secrets

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.urls import reverse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (UserCreateSerializer, UserReadSerializer,
                             FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeListSerializer,
                             SetAvatarSerializer, SetPasswordSerializer,
                             ShoppingCartSerializer, SubscribeSerializer,
                             SubscriptionSerializer, TagSerializer)
from ingredients.models import Ingredient
from recipes.models import IngredientInRecipes, Recipe
from tags.models import Tag

User = get_user_model()


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
        для остальных действий выбирает UserReadSerializer.
        Возвращает сериализатор для текущего действия.
        """
        if self.action == 'create':
            return UserCreateSerializer
        return UserReadSerializer

    def get_permissions(self):
        """Выбирает права доступа в зависимости от выполняемого действия.

        Для действия 'create' выбирает AllowAny, для действий 'me,
        subscriptions, subscribe, set_password, avatar' выбирает
        IsAuthenticated. Для всех остальных действий выбирает - AllowAny.
        """
        if self.action == 'create':
            self.permission_classes = (permissions.AllowAny,)
        elif self.action in {
            'me',
            'subscriptions',
            'subscribe',
            'set_password',
            'avatar',
        }:
            self.permission_classes = (permissions.IsAuthenticated,)
        else:
            self.permission_classes = (permissions.AllowAny,)
        return super().get_permissions()

    @action(detail=False)
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
        serializer = SubscribeSerializer(
            data={'user': request.user.pk, 'author': author.pk},
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def remove_subscribe(self, request, id=None):
        """Убирает подписку на автора."""
        author = self.get_object()
        subscription = request.user.subscriptions.filter(
            author=author,
        ).first()
        if not subscription:
            raise NotFound('Подписка не найдена.')
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def me(self, request):
        """Возвращает профиль текущего пользователя."""
        serializer = UserReadSerializer(
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
        favorite = recipe.favorites.filter(user=request.user).first()
        if not favorite:
            raise NotFound('Рецепт отсутствует в избранном.')
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
        cart_item = recipe.shopping_cart.filter(user=request.user).first()
        if not cart_item:
            raise NotFound('Рецепт отсутствует в списке покупок.')
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        """Генерирует короткую ссылку, если её ещё нет."""
        recipe = self.get_object()
        if not recipe.short_link:
            recipe.short_link = secrets.token_urlsafe(6)[:8]
            recipe.save(update_fields=['short_link'])
        relative_path = reverse(
            'short-link-redirect', args=[recipe.short_link]
        )
        full_url = request.build_absolute_uri(relative_path)
        return Response({'short-link': full_url})

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Скачивает файл со списком покупок."""
        ingredients = (
            IngredientInRecipes.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        content = '\n'.join([
            'Список покупок:',
            *(
                f'{ing["ingredient__name"]} '
                f'({ing["ingredient__measurement_unit"]})'
                f' - {ing["total_amount"]}'
                for ing in ingredients
            ),
        ])
        buffer = io.BytesIO(content.encode('utf-8'))
        buffer.seek(0)
        return FileResponse(
            buffer,
            content_type='text/plain; charset=utf-8',
            as_attachment=True,
            filename='shopping_cart.txt',
        )
