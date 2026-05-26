from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    """Модель тега для рецептов."""

    name = models.CharField(
        _('Название'),
        max_length=50,
        unique=True,
        help_text=_('Название тега')
    )
    color = models.CharField(
        _('Цвет'),
        default='#FF0000',
        help_text=_('Цвет в HEX формате (#RRGGBB)')
    )
    slug = models.SlugField(
        _('Слаг'),
        max_length=50,
        unique=True,
        help_text=_('Уникальный слаг для URL')
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ['name']

    def __str__(self):
        return self.name
