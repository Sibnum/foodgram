"""Фильтры DRF для API приложения Foodgram.

Содержит RecipeFilter — фильтр для рецептов по автору,
тегам (slug), избранному и списку покупок текущего пользователя.
"""

import django_filters
from django.db.models import Q

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов по автору, избранному, корзине и тегам."""

    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.CharFilter(method='filter_tags')
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, queryset, name, _):
        """Фильтрует рецепты по slug тегов в комбинации OR.

        Если выбрано несколько тегов, показываются рецепты,
        отмеченные хотя бы одним из этих тегов.
        """
        tags = self.request.GET.getlist('tags')
        if tags:
            query = Q()
            for tag_slug in tags:
                query |= Q(tags__slug=tag_slug)
            queryset = queryset.filter(query)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты по наличию в избранном у текущего пользователя."""
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты в списке покупок.

        Фильтрует рецепты по наличию в списке покупок у текущего
        пользователя.
        """
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
