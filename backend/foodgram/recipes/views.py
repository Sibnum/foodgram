from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Responce

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
            self.permission_classes = (permissions.IsAuthenticated,):
        elif self.action in ('partial_update', 'update', 'destroy'):
            self.permission_classes = (permissions.IsAuthenticated,):
        else:
            self.permission_classes = (permissions.AllowAny,)
        return super().get_permissons() 