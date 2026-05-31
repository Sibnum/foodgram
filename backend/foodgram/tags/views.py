from rest_framework import viewsets
from .models import Tag
from .serializers import TagSerializer


class TagViewSet(viewsets.ReadOnluModelViewSet):
    """Обрабатывает запросы GET /api/tags/ и GET /api/tags/{id}/."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
