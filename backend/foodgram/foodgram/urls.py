"""Главные маршруты (URL patterns) проекта Foodgram.

Подключает админку, API-маршруты и обработчик коротких ссылок.
"""
from django.contrib import admin
from django.urls import include, path

from recipes.views import redirect_by_short_link

urlpatterns = [
    path(
        'admin/',
        admin.site.urls
    ),
    path(
        'api/',
        include('api.urls')
    ),
    path(
        's/<slug:short_link>/',
        redirect_by_short_link,
        name='short-link-redirect'
    ),
]
