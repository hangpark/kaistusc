"""
사이트 관리 도구 어드민 페이지 설정.
"""

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Category, GroupServicePermission, Service, TopBanner


class CategoryAdmin(TranslationAdmin):
    """
    :class:`Category` 모델에 대한 커스텀 어드민.

    `django-modeltranlation` 에서 제공하는 :class:`TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """

    pass


class ServiceAdmin(TranslationAdmin):
    """
    `Service` 모델에 대한 커스텀 어드민.

    `django-modeltranlation` 에서 제공하는 :class:`TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """

    pass
    
class TopBannerAdmin(TranslationAdmin):
    """
    `TopBanner` 모델에 대한 커스텀 어드민.

    `django-modeltranlation` 에서 제공하는 :class:`TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """

    pass

admin.site.register(Category, CategoryAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(TopBanner, TopBannerAdmin)
admin.site.register(GroupServicePermission)
