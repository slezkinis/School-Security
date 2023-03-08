from django.contrib import admin
from .models import Person, UnknownEnterPerson


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(UnknownEnterPerson)
class UnknownPersonAdmin(admin.ModelAdmin):
    pass