"""
게시판 모델.
"""

import os

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from apps.manager.constants import *
from apps.manager.models import Service, ServiceManager
from kaistusc.settings import MEDIA_URL

# Post Activities
ACTIVITY_VIEW = 'VIEW'
ACTIVITY_VOTE = 'VOTE'


class Board(Service):
    """
    게시판을 구현한 모델.

    :class:`Service` 모델을 상속받아 메인페이지 노출여부를 추가로 저장합니다.
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


class PostActivity(models.Model):
    """
    포스트 활동을 구현한 모델.

    사용자가 포스트에 정해진 활동을 행하였다는 정보를 기록하는 모델입니다.
    :class:`User` 모델과 :class:`BasePost` 모델 사이의 중간모델 역할을
    수행합니다.

    포스트 조회나 추천/비추천 등 활동이 있을 수 있습니다. 기본적으로 사용자의
    포스트에 대한 활동은 각 포스트마다 최대 한 번 가능합니다.
    """

    user = models.ForeignKey(
        'auth.User',
        verbose_name=_("유저"),
        null=True)

    ip = models.CharField(
        _("IP 주소"),
        max_length=40)

    post = models.ForeignKey(
        'BasePost',
        verbose_name=_("포스트"))

    ACTIVITY_CHOICES = (
        (ACTIVITY_VIEW, _("조회")),
        (ACTIVITY_VOTE, _("추천/비추천")),
    )
    activity = models.CharField(
        _("활동구분"),
        max_length=4, choices=ACTIVITY_CHOICES)

    def save(self, *args, **kwargs):
        """
        사용자 활동을 저장하는 메서드.

        포스트에 해당 사용자가 같은 활동을 이미 진행한 경우 아무런 처리를 하지
        않습니다. 사용자가 로그인이 되어있지 않은 경우 중복활동 여부는 IP 주소로
        판단합니다.

        본 메서드는 중복활동 여부를 반환합니다. 이 반환값을 통해 추가 로직을
        구현할 수도 있습니다.
        """
        if self.user:
            is_new = not PostActivity.objects.filter(
                user=self.user, post=self.post,
                activity=self.activity).exists()
        else:
            is_new = not PostActivity.objects.filter(
                ip=self.ip, post=self.post, activity=self.activity).exists()
        if is_new:
            super().save(*args, **kwargs)
        return is_new


class Tag(models.Model):
    """
    게시글에 달리는 태그 모델.

    게시판별로 가능한 태그를 생성할 수 있습니다.
    """

    board = models.ForeignKey(
        Board,
        verbose_name=_("게시판"))

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


class BasePost(models.Model):
    """
    포스트를 정의하는 모델.

    게시글과 댓글 등 포스트에 해당하는 모델은 본 베이스 모델을 상속받아
    구현되었습니다. 본 모델은 강력한 포스트 권한 관리와 사용자 활동 관리
    기능을 제공합니다.
    """

    date = models.DateTimeField(
        _("등록일시"),
        auto_now_add=True)

    author = models.ForeignKey(
        'auth.User',
        verbose_name=_("작성자"),
        null=True)

    content = models.TextField(
        _("내용"))

    is_deleted = models.BooleanField(
        _("삭제글"),
        default=False)

    is_secret = models.BooleanField(
        _("비밀글"),
        default=False)

    involved_users = models.ManyToManyField(
        'auth.User',
        through=PostActivity, related_name='involved_posts',
        verbose_name=_("참여자"))

    vote_up = models.IntegerField(
        _("추천수"),
        default=0)

    vote_down = models.IntegerField(
        _("비추천수"),
        default=0)

    class Meta:
        ordering = ['-date']

    def is_owned_by(self, user):
        """
        주어진 사용자의 포스트인지 확인하는 메서드.
        """
        return self.author == user

    def is_permitted(self, user, permission):
        """
        주어진 사용자의 포스트 이용권한을 확인하는 메서드.

        본 메서드는 게시글, 댓글 등 여러 포스트 상속 모델들의 권한 설정을 손쉽게
        커스터마이징 할 수 있도록 :meth:`pre_permitted` 와
        :meth:`post_permitted` 메서드를 호출합니다. 이들은 기본적으로
        :const:`True` 를 반환하며, 포스트 상속 모델에서 두 메서드를 필요 시
        오버라이드 하는 방식으로 활용 가능합니다.
        """
        if user.is_superuser:
            return True
        if not self.pre_permitted(user, permission):
            return False
        if self.is_deleted:
            return False
        if self.is_owned_by(user):
            return True
        if self.is_secret:
            return False
        return self.post_permitted(user, permission)

    def pre_permitted(self, user, permission):
        """
        포스트 이용권한 확인 이전 필수적으로 있어야 하는 권한을 확인하는 메서드.
        """
        return True

    def post_permitted(self, user, permission):
        """
        포스트 이용권한 확인 후 관련 객체의 이용권한을 확인하는 메서드.
        """
        return True

    def get_activity_count(self, activity):
        """
        특정 활동을 진행한 사용자 총수를 반환하는 메서드.

        """
        return PostActivity.objects.filter(
            post=self, activity=activity).count()

    def get_hits(self):
        """
        조회수를 반환하는 메서드.
        """
        return self.get_activity_count(ACTIVITY_VIEW)

    def assign_activity(self, request, activity):
        """
        포스트에 특정 활동을 등록하는 메서드.

        :class:`PostActivity` 의 :meth:`save` 메서드와 동일합니다.
        """
        return PostActivity(
            user=request.user if request.user.is_authenticated else None,
            ip=request.META['REMOTE_ADDR'],
            post=self,
            activity=activity
        ).save()

    def assign_hits(self, request):
        """
        포스트 조회 활동을 등록하는 메서드.
        """
        self.assign_activity(request, ACTIVITY_VIEW)

    def attached_file(self):
        """
        포스트에 첨부된 첨부파일을 리턴하는 메서드.
        """
        return AttachedFile.objects.filter(post=self)



class Post(BasePost):
    """
    게시글을 구현한 모델.
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

    is_notice = models.BooleanField(
        _("공지글"),
        default=False)

    class Meta:
        verbose_name = _('포스트')
        verbose_name_plural = _('포스트(들)')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # return os.path.join(self.board.get_absolute_url(), str(self.id))
        return self.board.get_absolute_url()+'/'+str(self.id)

    def pre_permitted(self, user, permission):
        """
        게시글 권한 확인 이전에 게시판 접근권한을 확인하는 메서드.
        """
        return self.board.is_permitted(user, PERM_ACCESS)

    def post_permitted(self, user, permission):
        """
        게시글 권한 확인 이후에 동일 권한이 게시판에도 있는지 확인하는 메서드.
        """
        return self.board.is_permitted(user, permission)


class Comment(BasePost):
    """
    댓글을 구현한 모델.
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
        return os.path.join(
            self.parent_post.get_absolute_url(), "comment", str(self.id))

    def pre_permitted(self, user, permission):
        """
        댓글 권한 확인 이전에 게시글 읽기권한을 확인하는 메서드.
        """
        return self.parent_post.is_permitted(user, PERM_READ)

    def post_permitted(self, user, permission):
        """
        댓글 권한 확인 이후에 동일 권한이 게시판에도 있는지 확인하는 메서드.
        """
        return self.parent_post.board.is_permitted(user, permission)



def get_upload_path(instance, filename):
    """
    첨부파일이 업로드 되는 경로를 반환하는 함수.

    첨부파일은 포스트별로 다른 디렉토리에 저장됩니다.
    """
    return os.path.join("post-%d" % instance.post.id, filename)


class AttachedFile(models.Model):
    """
    포스트, 댓글 첨부파일을 구현한 모델.
    """

    post = models.ForeignKey(
        BasePost,
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
        """
        파일 크기를 반환하는 메서드.
        """
        try:
            return self.file.size
        except:
            return 0


@receiver(post_delete, sender=AttachedFile)
def delete_file(sender, instance, *args, **kwargs):
    """
    :class:`AttachedFile` 인스턴스가 삭제될 시 실제 저장된 첨부파일도 함께
    삭제하는 함수.
    """
    if os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
