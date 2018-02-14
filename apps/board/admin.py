"""
게시판 어드민 페이지 설정.
"""

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import AttachedFile, Board, BoardTab, Comment, Post, Tag, Banner, BannerCarousel, Link, ProjectPost, Schedule


class BoardAdmin(TranslationAdmin):
    """
    :class:`Board` 모델에 대한 커스텀 어드민.

    `django-modeltranslation` 에서 제공하는 :class:TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """

    pass

class BoardTabAdmin(TranslationAdmin):
    """
    :class:`BoardTab` 모델에 대한 커스텀 어드민.

    `django-modeltranslation` 에서 제공하는 :class:TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """
    pass

class TagAdmin(TranslationAdmin):
    """
    :class:`Tag` 모델에 대한 커스텀 어드민.

    `django-modeltranslation` 에서 제공하는 :class:TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """

    pass


class PostAdmin(TranslationAdmin):
    """
    :class:`Post` 모델에 대한 커스텀 어드민.

    `django-modeltranslation` 에서 제공하는 :class:TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """

    pass

class ScheduleInline(admin.TabularInline):
    model = Schedule
    fields = ('title', 'date')

class ProjectPostAdmin(TranslationAdmin):
    """
    :class:`ProjectPost` 모델에 대한 커스텀 어드민.

    `django-modeltranslation` 에서 제공하는 :class:TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """
    inlines = (ScheduleInline,)
    

class CommentAdmin(TranslationAdmin):
    """
    :class:`Comment` 모델에 대한 커스텀 어드민.

    `django-modeltranslation` 에서 제공하는 :class:TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """

    pass

class BannerAdmin(TranslationAdmin):
    """
    :class:`Banner` 모델에 대한 커스텀 어드민.

    `django-modeltranslation` 에서 제공하는 :class:TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """
    fields = ('title', 'url', 'image', 'author')

class BannerCarouselAdmin(TranslationAdmin):
    """
    :class:`BannerCarousel` 모델에 대한 커스텀 어드민.

    `django-modeltranslation` 에서 제공하는 :class:TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """

    pass

class LinkAdmin(TranslationAdmin):
    """
    :class:`Link` 모델에 대한 커스텀 어드민.

    `django-modeltranslation` 에서 제공하는 :class:TranslationAdmin` 을 상속받아
    다국어 처리를 사용자 친화적으로 변경하였습니다.
    """
    fields = ('url', 'text', 'author')

admin.site.register(Board, BoardAdmin)
admin.site.register(BoardTab, BoardTabAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(ProjectPost, ProjectPostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(BannerCarousel, BannerCarouselAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(AttachedFile)
