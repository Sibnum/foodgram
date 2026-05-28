from django.contrib import admin
from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Администрирование тегов.

    Предоставляет интерфейс для управления тегами рецептов:
    - Просмотр и редактирование тегов
    - Автоматическое заполнение slug из названия
    - Отображение количества рецептов по тегу
    """

    list_display = ('name', 'slug', 'recipe_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='Количество рецептов')
    def recipe_count(self, tag):
        """Возвращает количество рецептов с этим тегом."""
        return tag.recipe_set.count()
