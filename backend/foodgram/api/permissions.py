"""Разрешения (permissions) DRF для API приложения Foodgram.

Содержит IsAuthorOrReadOnly — разрешение, позволяющее
редактировать рецепт только его автору, остальным — только чтение.
"""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Только автор может редактировать свой рецепт."""

    def has_object_permission(self, request, view, recipe):
        if request.method in permissions.SAFE_METHODS:
            return True
        return recipe.author == request.user
