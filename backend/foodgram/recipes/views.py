from django.shortcuts import get_object_or_404, redirect

from .models import Recipe


def redirect_by_short_link(request, short_link):
    """Перенаправляет с короткой ссылки на страницу рецепта."""
    recipe = get_object_or_404(Recipe, short_link=short_link)
    return redirect(f'/recipes/{recipe.pk}/')
