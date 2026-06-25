"""Админ-панель для моделей приложения Рецепты."""

from django.contrib import admin

from .models import Favorite, IngredientInRecipes, Recipe, ShoppingCart


class SearchFieldsAdmin(admin.ModelAdmin):
    """Определяет базовые поля для поиска."""

    search_fields = ('user__username', 'recipe__name')


class IngredientInRecipesInline(admin.TabularInline):
    """Редактирование ингредиентов на странице рецептов."""

    model = IngredientInRecipes
    extra = 1
    min_num = 1
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Администрирование рецептов.

    Предоставляет интерфейс для управления рецептами:
    - Просмотр и редактирование рецептов
    - Редактирование ингредиентов с количеством на странице рецептов
    - Фильтрация по тегам и авторам
    - Отображение статистики (избранное список покупок)
    """

    list_display = (
        'name',
        'author',
        'cooking_time',
        'tags_list',
        'in_favorites_count',
        'in_shopping_carts_count',
    )
    list_filter = ('tags', 'author')
    search_fields = ('name', 'author__username')
    inlines = (IngredientInRecipesInline,)
    readonly_fields = ('short_link',)

    @admin.display(description='Теги')
    def tags_list(self, recipe):
        """Возвращает список тегов рецепта."""
        return ', '.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='В избранном')
    def in_favorites_count(self, recipe):
        """Возвращает количество избранного."""
        return recipe.favorites.count()

    @admin.display(description='В списке покупок')
    def in_shopping_carts_count(self, recipe):
        """Возвращает количество в списке покупок."""
        return recipe.shopping_cart.count()


@admin.register(Favorite)
class FavoriteAdmin(SearchFieldsAdmin):
    """Администрирование избранного.

    Предоставляет интерфейс для просмотра избранных рецептов пользователей.
    """

    list_display = ('user', 'recipe', 'created_at')
    list_filter = ('user',)


@admin.register(IngredientInRecipes)
class IngredientInRecipesAdmin(admin.ModelAdmin):
    """Администрирование ингредиентов в рецептах.

    Предоставляет интерфейс для управления количеством ингредиентов
    в рецептах.
    """

    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(SearchFieldsAdmin):
    """Администрирование списка покупок.

    Предоставляет интерфейс для просмотра списков покупок пользователей.
    """

    list_display = ('user', 'recipe', 'created_at')
    list_filter = ('user',)
