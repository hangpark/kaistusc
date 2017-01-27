from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from .permissions import *

# Basic service permissions
PERMISSION_CHOICES = (
    (PERMISSION_NONE, _("권한없음")),
    (PERMISSION_ACCESSIBLE, _("접근권한")),
    (PERMISSION_READABLE, _("읽기권한 (혹은 이에 준하는 특수권한)")),
    (PERMISSION_COMMENTABLE, _("댓글권한 (혹은 이에 준하는 특수권한)")),
    (PERMISSION_WRITABLE, _("쓰기권한 (혹은 이에 준하는 특수권한)")),
    (PERMISSION_EDITABLE, _("수정권한 (혹은 이에 준하는 특수권한)")),
    (PERMISSION_DELETABLE, _("삭제권한 (혹은 이에 준하는 특수권한)")),
)


class Category(models.Model):
    """
    홈페이지 구조에서 상위 단위로 카테고리를 정의한 모델.
    """

    name = models.CharField(
        _("카테고리명"),
        max_length=32, unique=True)

    is_open = models.BooleanField(
        _("사이트맵 노출여부"),
        default=True)

    class Meta:
        ordering = ['is_open']
        verbose_name = _('카테고리')
        verbose_name_plural = _('카테고리(들)')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        s = self.service_set.first()
        if s:
            return s.get_absolute_url()
        return '/'


class ServiceQuerySet(models.QuerySet):
    """
    Service에 대한 커스텀 query set.
    """

    def accessible_for(self, user):
        """
        특정 유저가 접근가능한 서비스를 필터링한다.
        """
        # 관리자 계정인 경우 모든 서비스 접근 가능
        if user.is_superuser:
            return self

        # 일반 유저의 경우 조건에 따라 서비스 필터링
        q = Q(max_permission_anon__gte=PERMISSION_ACCESSIBLE)
        if user.is_authenticated():
            q |= Q(max_permission_auth__gte=PERMISSION_ACCESSIBLE)
        q |= Q(
            groupservicepermission__permission__gte=PERMISSION_ACCESSIBLE,
            groupservicepermission__group__in=user.groups.all())
        q &= Q(is_closed=False)
        return self.filter(q).distinct()


class ServiceManager(models.Manager):
    """
    Service에 대한 커스텀 manager. Service와 ServiceQuerySet을 연결한다.
    """

    def get_queryset(self):
        return ServiceQuerySet(self.model, using=self._db)

    def accessible_for(self, user):
        return self.get_queryset().accessible_for(user)


class Service(models.Model):
    """
    홈페이지 구조에서 하위 단위인 메뉴를 정의한 모델.
    """

    name = models.CharField(
        _("서비스명"),
        max_length=32, unique=True)

    category = models.ForeignKey(
        Category,
        verbose_name=_("서비스가 속한 카테고리"))

    url = models.CharField(
        _("서비스 최상위 주소"),
        max_length=32, default='/',
        help_text=_("도메인 하위 경로만 적어주세요. /aaa/bbb 형식을 지켜주세요."))

    level = models.IntegerField(
        _("노출순서"),
        default=1,
        help_text=_("같은 카테고리 내 서비스 간의 노출순서"))

    description = models.TextField(
        _("서비스 설명"),
        blank=True)

    is_closed = models.BooleanField(
        _("서비스 중지여부"),
        default=False,
        help_text=_("설정 시 관리자를 제외한 모든 유저의 접속이 불가능합니다."))

    max_permission_anon = models.IntegerField(
        _("비로그인 유저의 최대 권한"),
        choices=PERMISSION_CHOICES, default=PERMISSION_NONE)

    max_permission_auth = models.IntegerField(
        _("로그인 유저의 최대 권한"),
        choices=PERMISSION_CHOICES, default=PERMISSION_READABLE)

    permitted_groups = models.ManyToManyField(
        'auth.Group',
        through='GroupServicePermission', related_name='permitted_services',
        verbose_name=_("그룹 권한"))

    # Custom Manager
    objects = ServiceManager()

    class Meta:
        ordering = ['category', 'level']
        verbose_name = _('서비스')
        verbose_name_plural = _('서비스(들)')

    def __str__(self):
        return self.category.name + "/" + self.name

    def get_absolute_url(self):
        return self.url

    def is_permitted(self, user, permission=PERMISSION_ACCESSIBLE):
        """
        주어진 유저가 접근할 수 있는 서비스인지 확인하는 함수.
        """

        if user.is_superuser:
            return True
        if self.is_closed:
            return False
        if permission <= self.max_permission_anon:
            return True
        if permission <= self.max_permission_auth:
            return user.is_authenticated()
        return (user.groups.all() & self.permitted_groups.filter(
            groupservicepermission__permission__gte=permission)).exists()


class GroupServicePermission(models.Model):
    """
    특정 그룹에 특정 서비스에 대한 특정 권한을 부여하는 모델.
    """

    group = models.ForeignKey(
        'auth.Group',
        on_delete=models.CASCADE,
        verbose_name=_("그룹"))

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name=_("서비스"))

    permission = models.IntegerField(
        _("권한"),
        choices=PERMISSION_CHOICES, default=PERMISSION_ACCESSIBLE)

    class Meta:
        ordering = ['service', 'permission', 'group']
        verbose_name = _('그룹별 서비스 이용권한')
        verbose_name_plural = _('그룹별 서비스 이용권한(들)')

    def __str__(self):
        return "%s - %s - %s" % (self.service, self.permission, self.group)
