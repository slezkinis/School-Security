from django.db import models


class Person(models.Model):
    name = models.CharField('Имя человека', max_length=100)
    picture = models.ImageField('Фото человека')
    is_enter = models.BooleanField('Внутри ли человек')

    class Meta:
        verbose_name = 'известный человек'
        verbose_name_plural = 'известные люди'

    def __str__(self) -> str:
        return self.name


class UnknownEnterPerson(models.Model):
    picture = models.ImageField('Фото человека')

    class Meta:
        verbose_name = 'неизвестный человек'
        verbose_name_plural = 'неизвестные люди'

    def __str__(self) -> str:
        return f'Unknown {self.id}'