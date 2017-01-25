from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import *

admin.site.register(Board)
