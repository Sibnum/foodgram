from django.contrib import admin
from django.urls import include, path

from recipes.views import redirect_by_short_link

api_patterns = [
    path('', include('tags.urls')),
    path('', include('ingredients.urls')),
    path('', include('recipes.urls')),
    path('', include('users.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path(
        'admin/',
        admin.site.urls
    ),
    path(
        'api/',
        include(api_patterns)
    ),
    path(
        's/<slug:short_link>/',
        redirect_by_short_link,
        name='short-link-redirect'
    ),
]
