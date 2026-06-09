import django_filters
from .models import Recipe


class CharFilterInFilter(
    django_filters.BaseInFilter,
    django_filters.CharFilter,
):
    """Фильтр для списка строковых значений через queryset params."""


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов по автору, избранному, корзине и тегам."""

    author = django_filters.NumberFilter(field_name='author__id')
    tags = CharFilterInFilter(
        field_name='tags__slug',
        method='filter_tags'
    )
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, queryset, name, value):
        """Фильтрует рецепты по slug тега."""
        if value:
            return queryset.filter(tags__slug__in=value).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты по наличию в избранном у текущего пользователя."""
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты.

        По наличию в списке покупок у текущего пользователя.
        """
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
