# Generated by Django 4.1.7 on 2024-10-31 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0019_room_roomcamera_roomassistant"),
    ]

    operations = [
        migrations.AlterField(
            model_name="closedroom",
            name="secret_key",
            field=models.CharField(
                max_length=100, unique=True, verbose_name="Секретный ключ камеры"
            ),
        ),
        migrations.AlterField(
            model_name="entercamera",
            name="secret_key",
            field=models.CharField(
                max_length=100, unique=True, verbose_name="Секретный ключ камеры"
            ),
        ),
        migrations.AlterField(
            model_name="exitcamera",
            name="secret_key",
            field=models.CharField(
                max_length=100, unique=True, verbose_name="Секретный ключ камеры"
            ),
        ),
        migrations.AlterField(
            model_name="roomassistant",
            name="secret_key",
            field=models.CharField(
                max_length=100, unique=True, verbose_name="Секретный ключ устройства"
            ),
        ),
        migrations.AlterField(
            model_name="roomcamera",
            name="secret_key",
            field=models.CharField(
                max_length=100, unique=True, verbose_name="Секретный ключ камеры"
            ),
        ),
    ]
