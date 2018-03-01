"""
서비스 관리 도구 모델.
"""

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from .constants import *

#: 서비스 기본 권한들.
PERMISSION_CHOICES = (
    (PERM_NONE, _("권한없음")),
    (PERM_ACCESS, _("접근권한")),
    (PERM_READ, _("읽기권한 (혹은 이에 준하는 특수권한)")),
    (PERM_COMMENT, _("댓글권한 (혹은 이에 준하는 특수권한)")),
    (PERM_WRITE, _("쓰기권한 (혹은 이에 준하는 특수권한)")),
    (PERM_EDIT, _("수정권한 (혹은 이에 준하는 특수권한)")),
    (PERM_DELETE, _("삭제권한 (혹은 이에 준하는 특수권한)")),
)


class Category(models.Model):
    """
    카테고리를 구현한 모델.

    사이트 구조 상 유사한 서비스들의 모임으로 카테고리를 정의합니다. 사이트맵의
    최상위 분류로 기능합니다.
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

    def get_absolute_url(self, user):
        """
        카테고리 내 접근 가능한 첫 번째 서비스의 URL을 반환하는 메서드.

        카테고리는 특정 뷰와 연결되어 있지 않습니다. 따라서 카테고리에 대한
        URL을 카테고리 내 첫 번째 서비스의 URL로 설정하였습니다.

        이는 사용자가 카테고리 이름을 페이지 상에서 클릭하였을 때 자동으로 내부
        서비스로 이동하는 기능 등에 활용될 수 있어 UX 향상에 도움이 됩니다.
        """
        s = self.service_set.accessible_for(user).first()
        if s:
            return s.get_absolute_url()
        return '/'

    def get_services(self, user):
        """
        카테고리 내 접근 가능한 서비스들을 반호나하는 메서드
        """
        s = self.service_set.accessible_for(user)
        return s

class TopBanner(models.Model):
    """
    탑배너를 구현한 모델
    """
    text = models.CharField(
        _("텍스트"),
        max_length=128)

    url = models.URLField(
        _("링크 URL"),
        blank=True, null=True)

    terminate_at = models.DateTimeField(
        _("노출종료일시"),
        blank=True, null=True,
        help_text=_("공란일경우, 직접 삭제시까지 노출됩니다"))
        
    class Meta:
        verbose_name = _('탑배너')
        verbose_name_plural = _('탑배너(들)')
    

class ServiceQuerySet(models.QuerySet):
    """
    서비스에 대한 커스텀 쿼리셋.

    사용자에 따른 접근가능 서비스 필터링을 지원하기 위한 커스텀 쿼리셋입니다.
    """

    def accessible_for(self, user):
        """
        특정 사용자가 접근가능한 서비스를 필터링한 쿼리셋을 반환하는 메서드.
        """
        # 관리자 계정인 경우 모든 서비스 접근 가능
        if user.is_superuser:
            return self

        # 일반 유저의 경우 조건에 따라 서비스 필터링
        q = Q(max_permission_anon__gte=PERM_ACCESS)
        if user.is_authenticated():
            q |= Q(max_permission_auth__gte=PERM_ACCESS)
        q |= Q(
            groupservicepermission__permission__gte=PERM_ACCESS,
            groupservicepermission__group__in=user.groups.all())
        q &= Q(is_closed=False)
        return self.filter(q).distinct()


class ServiceManager(models.Manager):
    """
    서비스에 대한 커스텀 매니저.

    사용자에 따른 접근가능 서비스 필터링을 지원하기 위한 커스텀 매니저입니다.
    """

    def get_queryset(self):
        return ServiceQuerySet(self.model, using=self._db)

    def accessible_for(self, user):
        """
        특정 사용자가 접근가능한 서비스를 필터링한 쿼리셋을 반환하는 메서드.
        """
        return self.get_queryset().accessible_for(user)

class BaseService(models.Model):
    """
    서비스 베이스를 구현한 모델.

    서비스는 사이트의 독립된 각 기능입니다. 사용자는 특정 서비스에 대한
    이용권한이 정해져 있으며, 본 모델에는 권한관리 기능이 구현되어 있습니다.
    이러한 강력한 권한관리 기능을 이용하기 위해 각 서비스는 본 모델을 상속받아
    구현될 수 있습니다.

    서비스의 권한에는 `apps.service.constants` 에 정의된 7가지가 있습니다.
    이들은 상하관계를 갖게 되며, 상위 권한이 있는 사용자는 하위 권한 모두를
    갖고 있는 것으로 판단합니다. 또한, 사용자가 여러 권한이 있을 경우 그 중 가장
    높은 권한을 갖고 있는 것으로 판단합니다.
    """

    name = models.CharField(
        _("타이틀"),
        max_length=32, unique=True)

    level = models.IntegerField(
        _("노출순서"),
        default=1,
        help_text=_("같은 카테고리 내 노출순서"))

    is_closed = models.BooleanField(
        _("중지여부"),
        default=False,
        help_text=_("설정 시 관리자를 제외한 모든 유저의 접속이 불가능합니다."))

    max_permission_anon = models.IntegerField(
        _("비로그인 유저의 최대 권한"),
        choices=PERMISSION_CHOICES, default=PERM_NONE)

    max_permission_auth = models.IntegerField(
        _("로그인 유저의 최대 권한"),
        choices=PERMISSION_CHOICES, default=PERM_READ)

    permitted_groups = models.ManyToManyField(
        'auth.Group',
        through='GroupServicePermission', related_name='permitted_services',
        verbose_name=_("그룹별 권한"))

    #: 커스텀 매니저
    objects = ServiceManager()

    def get_absolute_url(self):
        return self.url

    def is_permitted(self, user, permission=PERM_ACCESS):
        """
        특정 사용자에게 주어진 이용권한이 있는지 확인하는 메서드.
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


class Service(BaseService):
    """
    서비스를 구현한 모델.

    서비스는 사이트의 독립된 각 기능입니다. 사용자는 특정 서비스에 대한
    이용권한이 정해져 있으며, 본 모델에는 권한관리 기능이 구현되어 있습니다.
    이러한 강력한 권한관리 기능을 이용하기 위해 각 서비스는 본 모델을 상속받아
    구현될 수 있습니다.

    서비스의 권한에는 `apps.service.constants` 에 정의된 7가지가 있습니다.
    이들은 상하관계를 갖게 되며, 상위 권한이 있는 사용자는 하위 권한 모두를
    갖고 있는 것으로 판단합니다. 또한, 사용자가 여러 권한이 있을 경우 그 중 가장
    높은 권한을 갖고 있는 것으로 판단합니다.
    """

    url = models.CharField(
        _("최상위 주소"),
        max_length=100, default='/',
        help_text=_("도메인 하위 경로만 적어주세요. /aaa/bbb 형식을 지켜주세요. 특정 페이지에 리다이렉팅 할 서비스의 경우 https://www.google.com/ 형식을 해주시면 됩니다."))

    category = models.ForeignKey(
        Category,
        verbose_name=_("카테고리"))

    description = models.TextField(
        _("설명"),
        blank=True)

    #: 커스텀 매니저
    objects = ServiceManager()

    class Meta:
        ordering = ['category', 'level']
        verbose_name = _('서비스')
        verbose_name_plural = _('서비스(들)')

    def __str__(self):
        return self.category.name + "/" + self.name


class GroupServicePermission(models.Model):
    """
    그룹과 서비스 사이의 권한을 관리하는 중간모델.

    그룹과 서비스 사이의 다대다 관계에서 특정 그룹의 주어진 서비스에 대한 권한을
    관리하는 중간모델입니다.
    """

    group = models.ForeignKey(
        'auth.Group',
        on_delete=models.CASCADE,
        verbose_name=_("그룹"))

    service = models.ForeignKey(
        BaseService,
        on_delete=models.CASCADE,
        verbose_name=_("서비스"))

    permission = models.IntegerField(
        _("권한"),
        choices=PERMISSION_CHOICES, default=PERM_ACCESS)

    class Meta:
        ordering = ['service', 'permission', 'group']
        verbose_name = _('그룹별 서비스 이용권한')
        verbose_name_plural = _('그룹별 서비스 이용권한(들)')

    def __str__(self):
        return "%s - %s - %s" % (self.service, self.permission, self.group)
