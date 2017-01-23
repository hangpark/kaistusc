import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.manager.models import *
from kaistusc.settings import MEDIA_URL


class Board(Service):
    """
    서비스를 확장하여 게시판을 정의하는 모델.
    """

    is_main = models.BooleanField(
        _("메인페이지 노출여부"),
        default=False)


    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    게시글에 달리는 태그 모델.
    """

    name = models.CharField(
        _("태그명"),
        max_length=32, unique=True)

    abbr = models.CharField(
        _("태그 축약어"),
        max_length=16, unique=True,
        help_text=_("긴 태그명의 경우 태그명 대신 표시할 짧은 축약어입니다."))

    slug = models.CharField(
        _("태그 슬러그"),
        max_length=8, unique=True,
        help_text=_("URL 상 태그를 구분짓는 짧은 지시자입니다."))

    def __str__(self):
        return self.name


class PostBase(models.Model):
    """
    게시글, 댓글 등 포스트를 정의하는 모델.

    게시글과 댓글은 본 베이스 모델을 상속받아 구현한다.
    """

    date = models.DateTimeField(
        _("등록일시"),
        auto_now_add=True)

    author = models.ForeignKey(
        'auth.User',
        verbose_name=_("작성자"))

    content = models.TextField(
        _("내용"))

    is_deleted = models.BooleanField(
        _("삭제여부"),
        default=False)

    class Meta:
        ordering = ['-date']


class Post(PostBase):
    """
    게시글을 정의한 모델.
    """

    board = models.ForeignKey(
        Board,
        verbose_name=_("등록 게시판"))

    title = models.CharField(
        _("제목"),
        max_length=128)

    tag = models.ForeignKey(
        Tag,
        verbose_name=_("태그"),
        null=True, blank=True)

    is_secret = models.BooleanField(
        _("비공개 여부"),
        default=False)

    is_notice = models.BooleanField(
        _("공지사항 여부"),
        default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.board.get_absolute_url() + "%d/" % self.id


class Comment(PostBase):
    """
    댓글을 정의한 모델.
    """

    parent_post = models.ForeignKey(
        Post,
        verbose_name=_("상위 게시글"))

    class Meta:
        ordering = ['date']

    def __str__(self):
        return _("'%s'의 댓글") % self.post

    def get_absolute_url(self):
        return self.parent_post.get_absolute_url() + "#comment-id-%d" % self.id


def get_upload_path(instance, filename):
    return os.path.join("post-%d" % instance.post.id, filename)


class AttachedFile(models.Model):
    """
    게시글, 댓글 등 포스트에 삽입되는 첨부파일 모델.
    """

    post = models.ForeignKey(
        PostBase,
        verbose_name=_("연결된 포스트"))

    file = models.FileField(
        _("첨부파일"),
        upload_to=get_upload_path)

    def __str__(self):
        return os.path.basename(self.file.name)

    def get_absolute_url(self):
        return os.path.join(MEDIA_URL, self.file.name)
