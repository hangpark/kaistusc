import os

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from apps.manager.models import Service, ServiceManager
from apps.manager.constants import *
from kaistusc.settings import MEDIA_URL


# Post Activities
ACTIVITY_VIEW = 'VIEW'
ACTIVITY_VOTE = 'VOTE'

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


class PostActivity(models.Model):

    user = models.ForeignKey(
        'auth.User',
        verbose_name=_("유저"),
        null=True)

    ip = models.CharField(
        _("IP 주소"),
        max_length=40)

    post = models.ForeignKey(
        'PostBase',
        verbose_name=_("포스트"))

    ACTIVITY_CHOICES = (
        (ACTIVITY_VIEW, _("조회")),
        (ACTIVITY_VOTE, _("추천/비추천")),
    )
    activity = models.CharField(
        _("활동구분"),
        max_length=4, choices=ACTIVITY_CHOICES)

    def save(self, *args, **kwargs):
        if self.user:
            is_new = not PostActivity.objects.filter(
                user=self.user, post=self.post, activity=self.activity).exists()
        else:
            is_new = not PostActivity.objects.filter(
                ip=self.ip, post=self.post, activity=self.activity).exists()
        if is_new:
            super(PostActivity, self).save(*args, **kwargs)
        return is_new


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
        주어진 유저의 포스트인지 확인하는 함수.
        """

        return self.author == user

    def is_permitted(self, user, permission):
        """
        주어진 유저의 포스트 이용권한을 확인하는 함수.

        게시글이나 댓글 등 `PostBase`를 상속확장하는 모델에서
        `pre_permitted()`와 `post_permitted()`를 정의하여 사용한다.
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
        포스트 이용권한 확인 이전 필수적으로 있어야 하는 권한을 체크한다.
        """

        return True

    def post_permitted(self, user, permission):
        """
        포스트 이용권한 확인 후 계층관계에 있는 객체의 이용권한을 체크한다.
        """

        return True

    def get_activity_count(self, activity):
        return PostActivity.objects.filter(post=self, activity=activity).count()

    def get_hits(self):
        return self.get_activity_count(ACTIVITY_VIEW)

    def assign_activity(self, request, activity):
        return PostActivity(
            user=request.user if request.user.is_authenticated else None,
            ip=request.META['REMOTE_ADDR'],
            post=self,
            activity=activity
        ).save()

    def assign_hits(self, request):
        self.assign_activity(request, ACTIVITY_VIEW)


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

    def pre_permitted(self, user, permission):
        return self.board.is_permitted(user, PERM_ACCESS)

    def post_permitted(self, user, permission):
        return self.board.is_permitted(user, permission)


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
        return os.path.join(self.parent_post.get_absolute_url(), "comment", str(self.id))

    def pre_permitted(self, user, permission):
        return self.parent_post.is_permitted(user, PERM_READ)

    def post_permitted(self, user, permission):
        return self.parent_post.board.is_permitted(user, permission)


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
