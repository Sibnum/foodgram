"""Админ-панель для модели Ingredient."""

from django.contrib import admin

from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Администрирование ингредиентов.

    Предоставляет интерфейс для управления ингредиентами:
    - Просмотр и редактирование ингредиентов
    - Фильтрация по единицам измерения
    - Поиск по названию
    """

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
