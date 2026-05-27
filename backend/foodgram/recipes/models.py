from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from users.models import User
from ingredients.models import Ingredient
from tags.models import Tag


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор'),
        help_text=_('Автор публикации')
    )
    name = models.CharField(
        _('Название'),
        max_length=256,
        help_text=_('Название рецепта')
    )
    image = models.ImageField(
        _('Картинка'),
        upload_to='recipes/image/',
        help_text=_('Изображение блюда')
    )
    text = models.TextField(
        _('Описание'),
        help_text=_('Текстовое описание рецепта')
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipes',
        through_fields=('recipe', 'ingredient'),
        verbose_name=_('Ингредиенты'),
        help_text=_('Ингредиенты для приготовления')
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('Теги'),
        help_text=_('Теги рецепта')
    )
    cooking_time = models.PositiveSmallIntegerField(
        _('Время приготовления (в минутах)'),
        validators=[MinValueValidator(1)],
        help_text=_('Дата создания')
    )
    short_link = models.CharField(
        _('Короткая ссылка'),
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        help_text=_('Короткая ссылка на рецепт')
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ['-created_at']
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class IngredientInRecipes(models.Model):
    """Промежуточная модель для связи рецепта и ингредиента с количеством."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name=_('Рецепт')
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('Ингредиент'),
    )
    amount = models.PositiveSmallIntegerField(
        _('Количество'),
        validators=[MinValueValidator(1)],
        help_text=_('Количество ингредиента в рецепте')
    )

    class Meta:
        verbose_name = _('Ингредиент в рецепте')
        verbose_name_plural = _('Ингредиенты в рецепте')
        constraints = [
            models.UniqueConstraint(
                fields=['recipes', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    """Модель избранного (связь пользователей и рецепта)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Пользователь')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Рецепт')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата добавления')
    )

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранное'),
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'


class ShoppingCart(models.Model):
    """Модель списка покупок (связь пользователя и рецепта)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name=_('Пользователь')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name=_('Рецепт')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата добавления')
    )

    class Meta:
        verbose_name = _('Список покупок')
        verbose_name_plural = _('Список покупок')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'
