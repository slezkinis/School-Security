from django.contrib import admin
from .models import *


class RoomCameraInline(admin.TabularInline):
    model=RoomCamera

class RoomAssistantInline(admin.TabularInline):
    model=RoomAssistant


@admin.register(TemplatePerson)
class TemplatePersonAdmin(admin.ModelAdmin):
    pass


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display=['name', 'is_enter', "is_food_conected"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display=['name', 'is_enter']
    readonly_fields = ['id']

    def id(self, obj):
        return obj.id


@admin.register(UnknownEnterPerson)
class UnknownPersonAdmin(admin.ModelAdmin):
    pass


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(TelegramBotAdmins)
class TelegramBotAdminsAdmin(admin.ModelAdmin):
    pass


@admin.register(EnterCamera)
class EnterCameraAdmin(admin.ModelAdmin):
    pass


@admin.register(ExitCamera)
class ExitCameraAdmin(admin.ModelAdmin):
    pass

@admin.register(ClosedRoom)
class ClosedRoomAdmin(admin.ModelAdmin):
    pass

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    inlines = [RoomCameraInline, RoomAssistantInline]