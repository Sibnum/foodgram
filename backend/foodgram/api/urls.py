"""Маршруты (URL patterns) для API приложения Foodgram.

Регистрирует ViewSet'ы для рецептов, пользователей, тегов и ингредиентов
через DefaultRouter, а также подключает маршруты аутентификации djoser.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('users', UserViewSet, basename='user')
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
