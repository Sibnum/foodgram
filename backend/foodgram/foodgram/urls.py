from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('tags.urls')),
    path('api/', include('ingredients.urls')),
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]
