from rest_framework import serializers
from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения тегов (GET /api/tags/)."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
