from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Recipe, Favorite, ShoppingCart
from .serializers import (
    RecipeListSerializer,
    RecipeCreateSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer
)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Только автор может редактировать свой рецепт"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class RecipeViewSet(viewsets.ModelViewSet):
    """Отображает рецепты: CRUD, избранное, корзину, короткую ссылку."""

    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        """Выбирает нужный сериализатор для текущего запроса."""
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateSerializer

    def get_permissions(self):
        """Определяет набор разрешений для текущего запроса."""
        if self.action in ('create',):
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.action in ('partial_update', 'update', 'destroy'):
            self.permission_classes = (
                permissions.IsAuthenticated,
                IsAuthorOrReadOnly
            )
        else:
            self.permission_classes = (permissions.AllowAny,)
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Создаёт рецепт и возвращает полное представление."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(author=self.request.user)
        response_serializer = RecipeListSerializer(
            instance, context={'request': request}
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Обновляет рецепт и возвращает полное представление."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = RecipeListSerializer(
            instance,
            context={'request': request}
        )
        return Response(response_serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Обрабатывает добавление рецепта в избранные или удаление из него."""
        recipe = self.get_object()
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(
            Favorite,
            user=request.user,
            recipe=recipe
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Обрабатывает добавление или удаление продуктов из списка покупок."""
        recipe = self.get_object()
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        cart_item = get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=recipe
        )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET'])
    def get_link(self, request, pk=None):
        """Генерирует короткую ссылку, если её ещё нет."""
        recipe = self.get_object()
        if not recipe.short_link:
            import secrets
            recipe.short_link = secrets.token_urlsafe(6)[:8]
            recipe.save(update_fields=['short_link'])
        return Response({'short-link': recipe.short_link})
