"""
서비스 관리 도구 국제화 지원 모듈.

`django-modeltranslation` 을 이용하여 다국어 지원을 하는 모듈입니다.
"""

from modeltranslation.translator import TranslationOptions, register

from .models import Category, BaseService, Service, TopBanner


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    """
    :class:`Category` 모델에 대한 국제화 지원.
    """

    fields = ('name',)


@register(BaseService)
class BaseServiceTranslationOptions(TranslationOptions):
    """
    :class:`Service` 모델에 대한 국제화 지원.
    """

    fields = ('name',)

@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    """
    :class:`Service` 모델에 대한 국제화 지원.
    """

    fields = ()

@register(TopBanner)
class TopBannerTranslationOptions(TranslationOptions):
    """
    :class:`TopBanner` 모델에 대한 국제화 지원.
    """

    fields = ('text',)