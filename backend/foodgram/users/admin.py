from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Администрирование пользователей.

    Предоставляет интерфейс для управления пользователями:
    - Просмотр и редактирование профилей
    - Управление правами доступа (группы, staff, superuser)
    - Отображение статистики (количество рецептов, избранное)
    """
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'recipes_count'
    )
    list_filter = ('is_staff', 'is_active', 'is_chef')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('favorite_recipes_count',)

    @admin.display(description='Количество рецептов')
    def recipes_count(self, user):
        """Возвращает количество рецептов пользователя."""
        return user.recipes.count()

    @admin.display(description='Количество избранных рецептов')
    def favorite_recipes_count(self, user):
        """Возвращает количество избранных рецептов."""
        return user.favorite_recipes_count
