"""Разрешения (permissions) DRF для API приложения Foodgram.

Содержит IsAuthorOrReadOnly — разрешение, позволяющее
редактировать рецепт только его автору, остальным — только чтение.
"""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Только автор может редактировать свой рецепт."""

    def has_object_permission(self, request, view, recipe):
        """Возвращает ответ, является ли пользователь автором рецепта."""
        return (
            request.method in permissions.SAFE_METHODS
            or recipe.author == request.user
        )
