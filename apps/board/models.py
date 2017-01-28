import os

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from apps.manager.models import Service, ServiceManager
from apps.manager.permissions import *
from kaistusc.settings import MEDIA_URL


class Board(Service):
    """
    서비스를 확장하여 게시판을 정의하는 모델.
    """

    is_main = models.BooleanField(
        _("메인페이지 노출"),
        default=False)

    objects = ServiceManager()

    class Meta:
        verbose_name = _('게시판')
        verbose_name_plural = _('게시판(들)')

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

    class Meta:
        verbose_name = _('태그')
        verbose_name_plural = _('태그(들)')

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
        _("삭제글"),
        default=False)

    class Meta:
        ordering = ['-date']

    def is_owned_by(self, user):
        """
        주어진 유저의 포스트인지 확인하는 함수.

        익명 유저를 처리하기 위한 로직이 포함되어있다.
        """

        return user.is_authenticated() and self.author == user

    def is_permitted(self, user, permission):
        """
        주어진 유저의 포스트 이용권한을 확인하는 함수.

        게시글이나 댓글 등 `PostBase`를 상속확장하는 모델에서
        `get_base_board()`와 `get_base_post()`를 정의하여 사용한다.
        """

        base_board = self.get_base_board()
        base_post = self.get_base_post()
        if user.is_superuser:
            return True
        if base_board and not base_board.is_permitted(user, PERMISSION_ACCESSIBLE):
            return False
        if self.is_deleted:
            return False
        if self.is_owned_by(user):
            return True
        if base_board:
            res = base_board.is_permitted(user, permission)
        else:
            res = True
        if base_post and permission <= PERMISSION_COMMENTABLE:
            res &= not base_post.is_secret
        return res

    def get_base_board(self):
        """
        포스트가 속한 게시판이 있다면 이를 반환한다. 이 경우, 게시판의
        이용권한이 상속된다.
        """

        pass

    def get_base_post(self):
        """
        포스트들이 계층구조를 가질 때 최상위 포스트를 반환한다. 이 경우,
        해당 포스트의 `is_secret` 값이 상속된다.
        """

        pass


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
        _("비밀글"),
        default=False)

    is_notice = models.BooleanField(
        _("공지글"),
        default=False)

    class Meta:
        verbose_name = _('포스트')
        verbose_name_plural = _('포스트(들)')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return os.path.join(self.board.get_absolute_url(), str(self.id))

    def get_base_board(self):
        return self.board

    def get_base_post(self):
        return self


class Comment(PostBase):
    """
    댓글을 정의한 모델.
    """

    parent_post = models.ForeignKey(
        Post,
        verbose_name=_("상위 포스트"))

    class Meta:
        ordering = ['date']
        verbose_name = _('댓글')
        verbose_name_plural = _('댓글(들)')


    def __str__(self):
        return _("'%s'의 댓글") % self.parent_post

    def get_absolute_url(self):
        return self.parent_post.get_absolute_url() + "#comment-id-%d" % self.id

    def get_base_board(self):
        return self.post.get_base_board()

    def get_base_post(self):
        return self.post


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

    class Meta:
        verbose_name = _('첨부파일')
        verbose_name_plural = _('첨부파일(들)')

    def __str__(self):
        return os.path.basename(self.file.name)

    def get_absolute_url(self):
        return os.path.join(MEDIA_URL, self.file.name)

    def get_file_size(self):
        try:
            return self.file.size
        except:
            return 0


@receiver(post_delete, sender=AttachedFile)
def delete_file(sender, instance, *args, **kwargs):
    if os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
