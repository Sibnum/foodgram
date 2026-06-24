import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Декодирует base64-строку в файл изображения."""

    def to_internal_value(self, file_data):
        if isinstance(file_data, str) and file_data.startswith('data:image'):
            format, imgstr = file_data.split(';base64,')
            ext = format.split('/')[-1]
            name = f'{uuid.uuid4()}.{ext}'
            file_data = ContentFile(base64.b64decode(imgstr), name=name)
        return super().to_internal_value(file_data)
