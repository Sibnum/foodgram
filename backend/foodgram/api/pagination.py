"""Пагинация DRF для API приложения Foodgram.

Содержит LimitPaginator — пагинатор с поддержкой
query-параметра limit для настройки количества элементов на странице.
"""

from rest_framework.pagination import PageNumberPagination


class LimitPaginator(PageNumberPagination):
    """Собственный пагинатор с поддержкой параметра limit."""

    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 100
