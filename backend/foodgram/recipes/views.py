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