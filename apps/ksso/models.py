"""
KAIST 단일인증서비스 모델.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _


class PortalInfoManager(models.Manager):
    """
    :class:`PortalInfo` 에 대한 커스텀 매니저.

    KAIST 단일인증서비스를 통해 최초 로그인 한 사용자는 자신의 정보를 총학생회에
    제공하는 것에 동의해야 최종 가입이 됩니다. 만약 동의하지 않을 경우에는 자동
    탈퇴처리가 됩니다. 그러나, 동의여부를 묻는 페이지에서 사이트 접속을 종료하는
    등 동의/비동의 여부를 확인할 수 없는 경우가 있습니다. 이때 임시로
    저장되어있는 사용자 개인정보를 사이트 관리자가 임의로 활용하지 못하도록
    동의한 사용자만을 필터링하여 제공해야 합니다. 본 매니저가 해당 역할을
    수행하고 있습니다.
    """

    def get_queryset(self):
        """
        정보제공에 동의한 사용자만을 필터링한 쿼리셋을 반환하는 메서드.
        """
        return super().get_queryset().filter(is_signed_up=True)


class PortalInfo(models.Model):
    """
    사용자의 포탈 계정 정보를 저장하는 모델.
    """

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

    is_signed_up = models.BooleanField(
        _("정보제공 동의여부"),
        default=False,
        help_text=_(
            "정보제공에 반대하면 계정삭제 처리가 되나, 아직 동의여부를 "
            "선택하지 않은 최초가입자의 경우 의사표현 시까지 정보가 "
            "임시저장됩니다. 이 특수경우에는 정보를 활용하지 않아야 합니다."))

    #: 정보제공 동의한 사용자만 다루는 커스텀 매니저.
    objects = PortalInfoManager()

    #: 모든 사용자를 다루는 기존 매니저.
    all_objects = models.Manager()

    def __str__(self):
        return self.ku_kname

    @classmethod
    def create(cls, user, kaist_uid):
        """
        클래스 인스턴스 생성 메서드.

        사용자 인스턴스와 사용자 UID를 입력받습니다.
        """
        return cls(user=user, kaist_uid=kaist_uid)

    @property
    def enter_year(self):
        if self.ku_std_no and len(self.ku_std_no) == 8:
            return self.ku_std_no[2:4]
        return None
