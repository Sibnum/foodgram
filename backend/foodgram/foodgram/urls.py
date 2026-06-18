from django.contrib import admin
from django.urls import include, path

from recipes.views import redirect_by_short_link

api_patterns = [
    path('api/', include('tags.urls')),
    path('api/', include('ingredients.urls')),
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
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
