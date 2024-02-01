from django.core.management.base import BaseCommand
from carsshop.models import CarType, Car, Dealership
import random


class Command(BaseCommand):
    help = "Заполняет базу данных для использования приложения 1"

    def handle(self, *args, **kwargs):
        dealership, _ = Dealership.objects.get_or_create(
            name="GB",
        )

        for _ in range(10):
            car_type, _ = CarType.objects.get_or_create(
                name=f"JET-{random.randint(1, 100)}",
                brand="BMW",
                price=random.randint(1000, 2000),
            )
            car, _ = Car.objects.get_or_create(
                car_type=car_type, color="orange", year=random.randint(2000, 2023)
            )
            dealership.available_car_types.add(car_type)

        self.stdout.write(self.style.SUCCESS("Данные успешно добавлены в базу данных"))
