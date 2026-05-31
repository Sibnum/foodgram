from rest_framework import viewsets
from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Обрабатывает GET /api/ingredients/ и GET /api/ingredients/{id}/."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """Возвращает полный или фильтрованный по name queryset."""
        queryset = self.queryset
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartwith=name)
        return queryset
