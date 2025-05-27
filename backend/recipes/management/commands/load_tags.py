import csv

from core.constants import DEFAULT_TAGS_FILE, MAX_LENGTH_ROW_TAGS
from django.core.management.base import BaseCommand
from tqdm import tqdm

from recipes.models import Tag


class Command(BaseCommand):
    """Менеджер для загрузки тегов в БД."""
    help = 'Загружает теги из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            nargs='?',
            default=DEFAULT_TAGS_FILE,
            help='Путь к CSV файлу с тегами (по умолчанию — data/tags.csv)'
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        new_tags = []

        with open(file_path, encoding='utf-8') as file:
            reader = list(csv.reader(file))
            existing = set(Tag.objects.values_list('name', 'slug'))

            for row in tqdm(reader, desc='Загрузка тегов'):
                if len(row) != MAX_LENGTH_ROW_TAGS:
                    continue

                name, slug = row
                name = name.strip()
                slug = slug.strip()

                if (name, slug) not in existing:
                    new_tags.append(Tag(name=name, slug=slug))
                    existing.add((name, slug))

        Tag.objects.bulk_create(new_tags, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f'Загружено тегов: {len(new_tags)}'
        ))
