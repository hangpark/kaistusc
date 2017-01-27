from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Board, Tag, Post, Comment


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
