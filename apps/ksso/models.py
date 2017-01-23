from django.db import models
from django.utils.translation import ugettext_lazy as _


class PortalInfoManager(models.Manager):
    """
    약관에 동의한 회원에 한정된 manager.

    KAIST Single Auth Service 3.0에 따라 최초 로그인 한 유저는 자신의 정보를
    총학생회에 제공하는 것에 동의해야 최종 가입이 되며, 동의하지 않으면 자동
    탈퇴처리 된다. 그러나, 동의여부를 묻는 창에서 사이트 접속을 종료하는 등
    동의/비동의 여부를 확인할 수 없을 때 임시로 저장되어있는 정보를 사이트
    관리자가 임의로 활용하지 못하도록 동의한 유저만을 필터링하는 것이다.
    """

    def get_queryset(self):
        return super(PortalInfoManager, self).get_queryset().filter(
            is_signed_up=True)


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

    is_signed_up = models.BooleanField(
        _("정보제공 동의여부"),
        default=False,
        help_text=_("정보제공에 반대하면 계정삭제 처리가 되나, 아직 동의여부를 선택하지 않은 최초가입자의 경우 의사표현 시까지 정보가 임시저장됩니다. 이 특수경우에는 정보를 활용하지 않아야 합니다."))

    # Custom Manager
    objects = PortalInfoManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.ku_kname

    @classmethod
    def create(cls, user, kaist_uid):
        return cls(user=user, kaist_uid=kaist_uid)
