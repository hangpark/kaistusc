# -*- coding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class PortalInfo(models.Model):
    user = models.OneToOneField(
        'auth.User',
        primary_key=True, related_name='portal_info',
        verbose_name=_("유저 인스턴스"))

    kaist_uid = models.CharField(
        _("KAIST UID"),
        max_length=128, unique=True)

    ku_kname = models.CharField(
        _("이름"),
        max_length=128, blank=True)

    ku_acad_prog = models.CharField(
        _("과정"),
        max_length=32, blank=True)

    ku_std_no = models.CharField(
        _("학번"),
        max_length=32, blank=True)

    ku_psft_user_status_kor = models.CharField(
        _("학적상태"),
        max_length=32, blank=True)

    ku_born_date = models.CharField(
        _("생년월일"),
        max_length=32, blank=True)

    ku_sex = models.CharField(
        _("성별"),
        max_length=32, blank=True)

    ou = models.CharField(
        _("학과"),
        max_length=32, blank=True)

    mail = models.CharField(
        _("메일주소"),
        max_length=32, blank=True)

    mobile = models.CharField(
        _("전화번호"),
        max_length=32, blank=True)

    @classmethod
    def create(cls, user, kaist_uid):
        return cls(user=user, kaist_uid=kaist_uid)

    def __str__(self):
        return self.ku_kname
