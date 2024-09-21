from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

import random
import string


class Student(models.Model):
    name = models.CharField('Имя ученика', max_length=100)
    picture = models.ImageField('Фото ученика')
    is_enter = models.BooleanField('Внутри ли ученик')
    is_food_conected = models.BooleanField("Питается ли ученик в столовой", default=False)
    last_eat = models.DateField("Последний приём пищи", default=timezone.now, db_index=True) 
    last_enter = models.DateTimeField(
        'Последний вход ученика',
        default=timezone.now,
        db_index=True
    )

    last_exit = models.DateTimeField(
        'Последний выход ученика',
        default=timezone.now,
        db_index=True
    )

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'

    def __str__(self) -> str:
        return self.name

class Employee(models.Model):
    name = models.CharField('Имя сотрудника', max_length=100)
    picture = models.ImageField('Фото сотрудника')
    is_enter = models.BooleanField('Внутри ли сотрудник')
    access_level = models.IntegerField("Уровень доступа", default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    last_enter = models.DateTimeField(
        'Последний вход сотрудника',
        default=timezone.now,
        db_index=True
    )

    last_exit = models.DateTimeField(
        'Последний выход сотрудника',
        default=timezone.now,
        db_index=True
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self) -> str:
        return self.name

class UnknownEnterPerson(models.Model):
    picture = models.ImageField('Фото человека')
    last_enter = models.DateTimeField(
        'Последний вход человека',
        default=timezone.now,
        db_index=True
    )

    last_exit = models.DateTimeField(
        'Последний выход человека',
        default=timezone.now,
        db_index=True
    )
    
    class Meta:
        verbose_name = 'неизвестный человек'
        verbose_name_plural = 'неизвестные люди'

    def __str__(self) -> str:
        return f'Unknown {self.last_enter}'


class TemplatePerson(models.Model):
    picture = models.ImageField('Фото человека')
    last_seen = models.DateTimeField(
        'Последний вход человека',
        default=timezone.now,
        db_index=True
    )

    
class History(models.Model):
    title = models.CharField('Название', max_length=100)
    data_time = models.DateTimeField(
        'Последний выход человека',
        default=timezone.now,
        db_index=True
    )
    image = models.ImageField('Фото человека', upload_to='history/', blank=True)
    TYPE_CHOICE = (
        ("known_enter", "Известный вошёл"),
        ("known_exit", "Известный вышел"),
        ("unknown_enter", "Неизвестный вошёл"),
        ("unknown_exit", "Неизвестный вышел"),
        ("open_room", "Открытие комнаты"),
        ("clear_enter", "Очистка входящих"),
        ("another", "Другое")
    )
    history_type = models.CharField("Тип истории", choices=TYPE_CHOICE, max_length=100, default="another")

    class Meta:
        verbose_name = 'История входа/выхода'
        verbose_name_plural = 'Истории входа/выхода'

    def __str__(self) -> str:
        return f'{self.title} {self.data_time.astimezone()}'


class TelegramBotAdmins(models.Model):
    name = models.CharField('Имя человека', max_length=100, blank=True)
    telegram_id = models.IntegerField('ID в Telegram')

    class Meta:
        verbose_name = 'Админ Telegram'
        verbose_name_plural = 'Админ Telegram'
    
    def __str__(self) -> str:
        return str(f'{self.name} {self.telegram_id}')


class EnterCamera(models.Model):
    name = models.CharField("Название", max_length=100)
    secret_key = models.CharField("Секретный ключ камеры", max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Камера на вход"
        verbose_name_plural = "Камеры на вход"
    
class ExitCamera(models.Model):
    name = models.CharField("Название", max_length=100)
    secret_key = models.CharField("Секретный ключ камеры", max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Камера на выход"
        verbose_name_plural = "Камеры на выход"


class ClosedRoom(models.Model):
    name = models.CharField("Название", max_length=100)
    secret_key = models.CharField("Секретный ключ камеры", max_length=100)
    access_level = models.IntegerField("Мин. уровень доступа", default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    last_enter = models.DateTimeField(
        'Последний вход в комнату',
        default=timezone.now,
        db_index=True
    )
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Комната с замком"
        verbose_name_plural = "Комнаты с замком"