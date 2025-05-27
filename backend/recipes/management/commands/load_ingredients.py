import csv

from core.constants import MAX_LENGTH_ROW_INGREDIENTS, PATH_INGREDIENTS_CSV
from django.core.management.base import BaseCommand
from tqdm import tqdm

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            nargs='?',
            default=PATH_INGREDIENTS_CSV,
            help='Путь к CSV файлу (по умолчанию — из settings)'
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        new_ingredients = []

        with open(file_path, encoding='utf-8') as file:
            reader = list(csv.reader(file))
            existing = set(
                Ingredient.objects.values_list('name', 'measurement_unit')
            )

            for row in tqdm(reader, desc="Загрузка ингредиентов"):
                if len(row) != MAX_LENGTH_ROW_INGREDIENTS:
                    continue

                name, unit = row
                name = name.strip()
                unit = unit.strip()

                if (name, unit) not in existing:
                    new_ingredients.append(
                        Ingredient(name=name, measurement_unit=unit)
                    )
                    existing.add((name, unit))

        Ingredient.objects.bulk_create(new_ingredients, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f'Загружено ингредиентов: {len(new_ingredients)}'))
