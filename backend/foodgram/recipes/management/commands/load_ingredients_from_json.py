import os

from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from orjson import loads
from recipes.models import Ingredient, MeasurementUnit

from foodgram import settings


class Command(BaseCommand):
    """Команда для загрузки фикстур из json файла в модель"""

    help = "load fixtures from json file into model"

    def add_arguments(self, parser):
        """Извлекаем аргументы из строки команды"""
        parser.add_argument("path", nargs="+", type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        """Сохраняем в модель данные из json файла"""
        path = os.path.join(settings.BASE_DIR, "ingredients.json")
        with open(path, "r", encoding="utf-8") as data:
            ingredients = loads(data.read())

        measurement_unit = {value["measurement_unit"] for value in ingredients}
        bulk_measurement_unit = [
            MeasurementUnit(measurement_unit=value)
            for value in measurement_unit
        ]

        try:
            MeasurementUnit.objects.bulk_create(bulk_measurement_unit)
        except IntegrityError:
            print(
                "Импорт окончился ошибкой. Проверьте единицы измерения на "
                "уникальность"
            )
            raise

        bulk_ingredients = [
            Ingredient(
                name=value["name"],
                measurement_unit=MeasurementUnit.objects.get(
                    measurement_unit=value["measurement_unit"]
                ),
            )
            for value in ingredients
        ]

        try:
            Ingredient.objects.bulk_create(bulk_ingredients)
        except IntegrityError:
            print(
                "Импорт окончился ошибкой. Проверьте ингредиенты на "
                "уникальность"
            )
            raise

        print(
            f"Импорт прошел успешно добавлено {len(bulk_ingredients)} "
            f"ингредиентов и {len(bulk_measurement_unit)} единиц измерения"
        )
