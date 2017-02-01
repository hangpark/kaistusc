from modeltranslation.translator import TranslationOptions, register

from .models import BasePost, Board, Comment, Post, Tag


@register(Board)
class BoardTranslationOptions(TranslationOptions):
    fields = ()


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name', 'abbr')


@register(BasePost)
class BasePostTranslationOptions(TranslationOptions):
    fields = ('content',)


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Comment)
class CommentTranslationOptions(TranslationOptions):
    fields = ()
