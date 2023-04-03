from django.contrib import admin
from .models import Person, UnknownEnterPerson, History, TelegramBotAdmins


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(UnknownEnterPerson)
class UnknownPersonAdmin(admin.ModelAdmin):
    pass


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(TelegramBotAdmins)
class TelegramBotAdminsAdmin(admin.ModelAdmin):
    pass