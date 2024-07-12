from django.contrib import admin
from .models import Person, UnknownEnterPerson, History, TelegramBotAdmins, TemplatePerson


@admin.register(TemplatePerson)
class TemplatePersonAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display=['name', 'is_enter', "is_food_conected"]


@admin.register(UnknownEnterPerson)
class UnknownPersonAdmin(admin.ModelAdmin):
    pass


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(TelegramBotAdmins)
class TelegramBotAdminsAdmin(admin.ModelAdmin):
    pass