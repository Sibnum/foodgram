from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    """Модель тега для рецептов."""

    name = models.CharField(
        verbose_name=_('Название'),
        max_length=32,
        unique=True,
        help_text=_('Название тега'),
    )
    slug = models.SlugField(
        verbose_name=_('Слаг'),
        max_length=32,
        null=True,
        unique=True,
        help_text=_('Уникальный слаг для URL'),
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ['name']

    def __str__(self):
        """Возвращает название тега."""
        return self.name
