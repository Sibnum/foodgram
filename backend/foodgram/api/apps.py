"""Настройки конфигурации приложения API.

Этот модуль содержит настройки конфигурации приложения API.
"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Класс конфигурации для приложения API.

    Определяет настройки приложения API.
    Описывает имя приложения и отображаемое имя.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'АПИ'
