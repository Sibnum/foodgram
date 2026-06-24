"""Модель ингредиента для приложения Foodgram."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        verbose_name=_('Название'),
        max_length=128,
        unique=True,
        help_text=_('Название ингредиента')
    )
    measurement_unit = models.CharField(
        verbose_name=_('Единица измерения'),
        max_length=64,
        help_text=_('Единица измерения (г, мл, шт. и т.д.)')
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('name',)

    def __str__(self):
        """Возвращает название ингредиента."""
        return self.name
