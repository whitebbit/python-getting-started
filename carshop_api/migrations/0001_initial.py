# Generated by Django 5.0 on 2024-01-28 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MonoSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_key', models.CharField(max_length=100, unique=True)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]