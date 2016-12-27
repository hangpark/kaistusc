from django.contrib import admin

from .models import Category, GroupMenuPermission, Menu

admin.site.register(Category)
admin.site.register(Menu)
admin.site.register(GroupMenuPermission)
