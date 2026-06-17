from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Favorite, Recipe, ShoppingCart
from .serializers import (FavoriteSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, ShoppingCartSerializer)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Только автор может редактировать свой рецепт"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class RecipeViewSet(viewsets.ModelViewSet):
    """Отображает рецепты: CRUD, избранное, корзину, короткую ссылку."""

    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter

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
        elif self.action in (
            'favorite',
            'shopping_cart',
            'download_shopping_cart',
        ):
            self.permission_classes = (permissions.IsAuthenticated,)
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

        favorite = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()
        if not favorite:
            return Response(
                {'errors': 'Рецепт отсутствует в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
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

        cart_item = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()
        if not cart_item:
            return Response(
                {'errors': 'Рецепт отсутствует в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST
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
        full_url = request.build_absolute_uri(f'/s/{recipe.short_link}/')
        return Response({'short-link': full_url})

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[permissions.IsAuthenticated]
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


def redirect_by_short_link(request, short_link):
    """Перенаправляет с короткой ссылки на страницу рецепта."""
    recipe = get_object_or_404(Recipe, short_link=short_link)
    return redirect(f'/recipes/{recipe.pk}/')
