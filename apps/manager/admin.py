from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Category, GroupServicePermission, Service


class CategoryAdmin(TranslationAdmin):
    pass


class ServiceAdmin(TranslationAdmin):
    pass


admin.site.register(Category, CategoryAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(GroupServicePermission)
