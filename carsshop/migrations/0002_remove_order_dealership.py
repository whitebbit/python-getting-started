# Generated by Django 4.2.5 on 2023-11-08 13:26

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("carsshop", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="dealership",
        ),
    ]