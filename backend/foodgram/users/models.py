from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator


class User(AbstractUser):
    """Собственная модель пользователя для Foodgram.

    Наследуется от AbstractUser и добавляет дополнительные поля.
    """

    first_name = models.CharField(
        _('Имя'),
        max_length=150,
        blank=False,
        help_text=_('Обязательное поле. Максимум 150 символов.')
    )
    last_name = models.CharField(
        _('Фамилия'),
        max_length=150,
        blank=False,
        help_text=_('Обязательное поле. Максимум 150 символов.')
    )
    email = models.EmailField(
        _('Адрес электронной почты'),
        blank=False,
        unique=True,
        help_text=_('Обязательное поле. Укажите действующий email.')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар'),
        help_text=_('Загрузите изображение для аватара')
    )
    bio = models. TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Биография'),
        help_text=_('Расскажите о себе')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Телефон'),
        help_text=_('Номер телефона в формате +7 ХХХ ХХХ ХХ ХХ')
    )
    website = models.URLField(
        max_length=200,
        blank=True,
        verbose_name=_('Веб-сайт'),
        help_text=_('Ссылка на ваш сайт или блог')
    )
    is_chef = models.BooleanField(
        default=False,
        verbose_name=_('Шеф-повар'),
        help_text=_('Отметьте, если вы профессиональный повар')
    )
    favorite_recipes_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Количество избранных рецептов')
    )

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-date_joined']

    def __str__(self):
        """Возвращает имя пользователя."""
        return self.username

    @property
    def full_name(self):
        """Возвращает полное имя пользователя."""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def clean(self):
        """Валидация модели."""
        super().clean()
        if self.email:
            self.email = self.email.lower().strip()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
