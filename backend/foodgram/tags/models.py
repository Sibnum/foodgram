from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    """Модель тега для рецептов."""

    name = models.CharField(
        _('Название')
    )

