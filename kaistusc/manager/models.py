# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['is_open']
        verbose_name = _('카테고리')
        verbose_name_plural = _('카테고리')


class MenuQuerySet(models.QuerySet):
    """
    Menu에 대한 커스텀 query set.
    """

    def available_for(self, user):
        """
        특정 유저가 접근가능한 메뉴를 필터링한다.
        """
        q_default = Q(is_open=True)
        q_user = Q(groupmenupermission__group__in=user.groups.all())
        return self.filter(q_default | q_user).distinct()


class MenuManager(models.Manager):
    """
    Menu에 대한 커스텀 manager. Menu와 MenuQuerySet을 연결한다.
    """

    def get_queryset(self):
        return MenuQuerySet(self.model, using=self._db)

    def available_for(self, user):
        return self.get_queryset().available_for(user)


class Menu(models.Model):
    """
    홈페이지 구조에서 하위 단위인 메뉴를 정의한 모델.
    """

    name = models.CharField(
        _("메뉴명"),
        max_length=32, unique=True)

    category = models.ForeignKey(
        Category,
        verbose_name=_("메뉴가 속한 카테고리"))

    url = models.CharField(
        _("메뉴 최상위 주소"),
        max_length=32, default='/',
        help_text=_("도메인 하위 경로만 적어주세요."))

    level = models.IntegerField(
        _("노출순서"),
        default=1,
        help_text=_("같은 카테고리 메뉴들 간의 노출순서"))

    is_open = models.BooleanField(
        _("사이트맵 노출여부"),
        default=True)

    accessible_groups = models.ManyToManyField(
        'auth.Group',
        through='GroupMenuPermission', related_name='accessible_menus',
        verbose_name=_("접근가능그룹"))

    # Custom Manager
    objects = MenuManager()

    def __str__(self):
        return self.category.name + "/" + self.name

    class Meta:
        ordering = ['category', 'is_open', 'level']
        verbose_name = _('메뉴')
        verbose_name_plural = _('메뉴')


class GroupMenuPermission(models.Model):
    """
    특정 그룹에 특정 메뉴에 대한 접근권한을 부여하는 모델.
    """

    group = models.ForeignKey(
        'auth.Group',
        on_delete=models.CASCADE,
        verbose_name=_("그룹"))

    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        verbose_name=_("메뉴"))

    def __str__(self):
        return "%s - %s" % (self.menu, self.group)

    class Meta:
        ordering = ['menu', 'group']
        verbose_name = _('그룹별 메뉴 접근권한')
        verbose_name_plural = _('그룹별 메뉴 접근권한')
