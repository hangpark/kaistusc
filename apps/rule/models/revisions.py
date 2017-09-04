from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _

from .rules import Rule, Chapter, Article


class Discussion(models.Model):
    """
    조문 및 이외 규정 구성 단위에 대한 논의사항.
    """
    rule = models.ForeignKey(
        Rule,
        verbose_name=_('규정'),
        related_name='discussions',
        null=True, blank=True,
        on_delete=models.SET_NULL)

    chapter = models.ForeignKey(
        Chapter,
        verbose_name=_('챕터'),
        related_name='discussions',
        null=True, blank=True,
        on_delete=models.SET_NULL)

    article = models.ForeignKey(
        Article,
        verbose_name=_('조항'),
        related_name='discussions',
        null=True, blank=True,
        on_delete=models.SET_NULL)

    from_committee = models.BooleanField(
        _('위원회 논의여부'),
        default=False)

    subject = models.CharField(
        _('주제'),
        max_length=64)

    author = models.ForeignKey(
        User,
        verbose_name=_('작성자'))

    date_created = models.DateField(
        _('작성일'),
        auto_now_add=True)

    date_modified = models.DateField(
        _('최종 수정일'),
        auto_now=True)

    @property
    def d_comments(self):
        return self.comments.all()

    class Meta:
        ordering = ['-from_committee']
        verbose_name = _('논의사항')
        verbose_name_plural = _('논의사항(들)')

    def get_rule_item(self):
        return self.article or self.chapter or self.rule


class Comment(models.Model):
    """
    논의주제에 대한 토막글.
    """
    discussion = models.ForeignKey(
        Discussion,
        verbose_name=_('논의'),
        related_name='comments')

    body = models.TextField(
        _('내용'),
        null=True, blank=True)

    author = models.ForeignKey(
        User,
        verbose_name=_('작성자'))

    date_created = models.DateField(
        _('작성일'),
        auto_now_add=True)

    date_modified = models.DateField(
        _('최종 수정일'),
        auto_now=True)

    class Meta:
        verbose_name = _('논의댓글')
        verbose_name_plural = _('논의댓글(들)')
