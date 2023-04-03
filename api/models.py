from django.db import models
from django.utils import timezone


class Person(models.Model):
    name = models.CharField('Имя человека', max_length=100)
    picture = models.ImageField('Фото человека')
    is_enter = models.BooleanField('Внутри ли человек')
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
        verbose_name = 'известный человек'
        verbose_name_plural = 'известные люди'

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


class History(models.Model):
    title = models.CharField('Название', max_length=100)
    data_time = models.DateTimeField(
        'Последний выход человека',
        default=timezone.now,
        db_index=True
    )
    image = models.ImageField('Фото человека', upload_to='history/', blank=True)


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