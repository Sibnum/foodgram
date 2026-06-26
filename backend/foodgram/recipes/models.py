"""Модели приложения Рецепты."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ingredients.models import Ingredient
from tags.models import Tag
from users.models import User


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор'),
        help_text=_('Автор публикации'),
    )
    name = models.CharField(
        verbose_name=_('Название'),
        max_length=256,
        help_text=_('Название рецепта'),
    )
    image = models.ImageField(
        verbose_name=_('Изображение'),
        upload_to='recipes/image/',
        help_text=_('Изображение блюда'),
    )
    text = models.TextField(
        verbose_name=_('Описание'),
        help_text=_('Описание рецепта'),
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipes',
        through_fields=('recipe', 'ingredient'),
        verbose_name=_('Ингредиенты'),
        help_text=_('Ингредиенты для приготовления'),
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('Теги'),
        help_text=_('Теги рецепта'),
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=_('Время приготовления'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(
                1440,
                message=_(
                    'Время приготовления не может превышать 24 часа'
                    ' (1440 минут)'
                )
            )
        ],
        help_text=_('Время приготовления рецепта в минутах'),
    )
    short_link = models.CharField(
        verbose_name=_('Короткая ссылка'),
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        help_text=_('Короткая ссылка на рецепт'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания'),
        help_text=_('Дата и время создания рецепта'),
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('-created_at',)
        default_related_name = 'recipes'

    def __str__(self):
        """Возвращает название рецепта."""
        return self.name


class IngredientInRecipes(models.Model):
    """Промежуточная модель для связи рецепта и ингредиента с количеством."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name=_('Рецепт'),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('Ингредиент'),
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name=_('Количество'),
        validators=[MinValueValidator(1)],
        help_text=_('Количество ингредиента в рецепте'),
    )

    class Meta:
        verbose_name = _('Ингредиент в рецепте')
        verbose_name_plural = _('Ингредиенты в рецепте')
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            )
        ]

    def __str__(self):
        """Возвращает название ингредиента с указанием кол-ва и мерой."""
        return (
            f'{self.ingredient.name} - {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class CreatedAtMixin(models.Model):
    """Абстрактный миксин, добавляющий поле created_at."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата добавления'),
    )

    class Meta:
        abstract = True


class Favorite(CreatedAtMixin):
    """Модель избранного (связь пользователей и рецепта)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Пользователь'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Рецепт'),
    )

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранное')
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite',
            )
        ]

    def __str__(self):
        """Возвращает имя пользователя -> название рецепта (избранное)."""
        return f'{self.user.username} -> {self.recipe.name} (избранное)'


class ShoppingCart(CreatedAtMixin):
    """Модель списка покупок (связь пользователя и рецепта)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name=_('Пользователь'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name=_('Рецепт'),
    )

    class Meta:
        verbose_name = _('Список покупок')
        verbose_name_plural = _('Списки покупок')
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart',
            )
        ]

    def __str__(self):
        """Возвращает имя пользователя -> название рецепта (список покупок)."""
        return f'{self.user.username} -> {self.recipe.name} (список покупок)'
