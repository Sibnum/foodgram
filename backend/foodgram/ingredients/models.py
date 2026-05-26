from django.db import models
from django.utils.translation import gettext_lazy as _


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        _('Название'),
        max_length=200,
        unique=True,
        help_text=_('Название ингредиента')
    )
    measurement_unit = models.CharField(
        _('Единица измерения'),
        max_length=50,
        help_text=_('Единица измерения (г, мл, шт. и т.д.)')
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ['name']
