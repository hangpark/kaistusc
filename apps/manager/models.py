# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

# Service access permissions
PERMISSION_ALL_USERS = 'ALL'
PERMISSION_LOGGED_IN_USERS = 'LOG'
PERMISSION_ACCESSIBLE_GROUPS = 'GRP'
PERMISSION_CLOSED = 'CLS'


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
        q = Q(permission=PERMISSION_ALL_USERS)
        if user.is_authenticated():
            q |= Q(permission=PERMISSION_LOGGED_IN_USERS)
        q |= Q(permission=PERMISSION_ACCESSIBLE_GROUPS,
            groupservicepermission__group__in=user.groups.all())
        q &= ~Q(permission=PERMISSION_CLOSED)
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
        help_text=_("도메인 하위 경로만 적어주세요."))

    level = models.IntegerField(
        _("노출순서"),
        default=1,
        help_text=_("같은 카테고리 내 서비스 간의 노출순서"))

    PERMISSION_CHOICES = (
        (PERMISSION_ALL_USERS, _("모든 유저")),
        (PERMISSION_LOGGED_IN_USERS, _("로그인 한 유저")),
        (PERMISSION_ACCESSIBLE_GROUPS, _("접근허가 그룹")),
        (PERMISSION_CLOSED, _("비공개")),
    )
    permission = models.CharField(
        _("서비스 이용권한"),
        max_length=3, choices=PERMISSION_CHOICES, default='ALL',
        help_text=_("접근허가 그룹 이외의 옵션으로 설정할 경우 서비스별 접근허가 그룹 설정이 적용되지 않습니다."))

    accessible_groups = models.ManyToManyField(
        'auth.Group',
        through='GroupServicePermission', related_name='accessible_services',
        verbose_name=_("접근허가 그룹"))

    # Custom Manager
    objects = ServiceManager()

    class Meta:
        ordering = ['category', 'permission', 'level']
        verbose_name = _('서비스')
        verbose_name_plural = _('서비스(들)')

    def __str__(self):
        return self.category.name + "/" + self.name

    def get_absolute_url(self):
        return self.url

    def is_accessible(self, user):
        """
        주어진 유저가 접근할 수 있는 서비스인지 확인하는 함수.
        """
        if user.is_superuser:
            return True
        if self.permission == PERMISSION_ALL_USERS:
            return True
        if self.permission == PERMISSION_LOGGED_IN_USERS:
            return user.is_authenticated()
        if self.permission == PERMISSION_ACCESSIBLE_GROUPS:
            return (user.groups.all() & self.accessible_groups.all()).exists()
        return False


class GroupServicePermission(models.Model):
    """
    특정 그룹에 특정 서비스에 대한 접근권한을 부여하는 모델.
    """

    group = models.ForeignKey(
        'auth.Group',
        on_delete=models.CASCADE,
        verbose_name=_("그룹"))

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name=_("서비스"))

    class Meta:
        ordering = ['service', 'group']
        verbose_name = _('그룹별 서비스 접근권한')
        verbose_name_plural = _('그룹별 서비스 접근권한(들)')

    def __str__(self):
        return "%s - %s" % (self.service, self.group)
