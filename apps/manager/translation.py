from modeltranslation.translator import TranslationOptions, register

from .models import Category, Service


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('name',)
