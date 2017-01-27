from modeltranslation.translator import TranslationOptions, register

from .models import Board, Tag, PostBase, Post, Comment


@register(Board)
class BoardTranslationOptions(TranslationOptions):
    fields = ()


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name', 'abbr')


@register(PostBase)
class PostBaseTranslationOptions(TranslationOptions):
    fields = ('content',)


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Comment)
class CommentTranslationOptions(TranslationOptions):
    fields = ()
