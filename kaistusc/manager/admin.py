from django.contrib import admin

from .models import Category, GroupServicePermission, Service

admin.site.register(Category)
admin.site.register(Service)
admin.site.register(GroupServicePermission)
