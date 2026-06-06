"""
Импорт данных из СSV файлов в Django ORM.

Этот скрипт читает CSV файл из директории foodgram/data/ и сохраняет данные в
соответствующие модели Django.

Пример использования:
    python manage.py import_data
    python manage.py import_data --path=/my/path/ingredients.csv
"""
import csv

from django.core.management.base import BaseCommand
from foodgram.settings import BASE_DIR
from ingredients.models import Ingredient


DATA_DIR = BASE_DIR.parent.parent / 'data'


class Command(BaseCommand):
    """Команда для импорта ингредиентов из CSV в БД."""
    help = 'Импортирует ингредиенты из СSV в БД'

    def add_arguments(self, parser):
        """Добавляет аргументы для запуска команды импортирования."""
        parser.add_argument(
            '--path',
            type=str,
            default=str(DATA_DIR / 'ingredients.csv'),
            help='Путь к CSV-файлу с ингредиентами',
        )

    def handle(self, *args, **options):
        """Импортирует ингредиенты."""
        file_path = options['path']
        self._import_from_csv(file_path)

    def _import_from_csv(self, file_path):
        """Импортирует ингредиенты."""
        self.stdout.write('Импортируем ингредиенты из CSV...')
        ingredients_to_create = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name = row[0].strip()
                measurement_unit = row[1].strip()
                ingredients_to_create.append(
                    Ingredient(name=name, measurement_unit=measurement_unit)
                )
        created_count = Ingredient.objects.bulk_create(
            ingredients_to_create,
            ignore_conflicts=True,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Импортировано {len(created_count)} ингредиентов. '
                f'Всего в БД: {Ingredient.objects.count()}.'
            )
        )
