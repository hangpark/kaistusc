from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import AttachedFile, Board, Comment, Post, Tag


class BoardAdmin(TranslationAdmin):
    pass


class TagAdmin(TranslationAdmin):
    pass


class PostAdmin(TranslationAdmin):
    pass


class CommentAdmin(TranslationAdmin):
    pass


admin.site.register(Board, BoardAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(AttachedFile)
