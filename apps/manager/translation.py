"""
서비스 관리 도구 국제화 지원 모듈.

`django-modeltranslation` 을 이용하여 다국어 지원을 하는 모듈입니다.
"""

from modeltranslation.translator import TranslationOptions, register

from .models import Category, Service


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    """
    `Category` 모델에 대한 국제화 지원.
    """

    fields = ('name',)


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    """
    `Service` 모델에 대한 국제화 지원.
    """

    fields = ('name',)
