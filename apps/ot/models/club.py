from django.db import models


class Club(models.Model):
    """
    동아리 정보
    """

    class Meta:
        verbose_name = '동아리 정보'
        verbose_name_plural = '동아리 정보(들)'

    def __str__(self):
        return str(self.name)

    name = models.CharField(
        max_length=63,
        verbose_name='동아리 이름',
    )
    pages = models.TextField(
        blank=True,
        verbose_name='동아리 페이스북/유튜브 페이지 주소',
    )
    one_line_intro = models.TextField(
        blank=True,
        verbose_name='동아리 한 줄 소개(메인 화면)',
    )
    intro = models.TextField(
        verbose_name='동아리 소개',
    )
    is_band = models.BooleanField(
        default=False,
        verbose_name='밴드 여부',
    )

    video_url1 = models.CharField(
        blank=True,
        max_length=63,
        verbose_name='동아리 소개 비디오 주소 #1',
    )
    video_url2 = models.CharField(
        blank=True,
        max_length=63,
        verbose_name='동아리 소개 비디오 주소 #2',
    )


class Image(models.Model):
    """
    동아리 홍보 사진
    """
    class Meta:
        verbose_name = '동아리 홍보 사진'
        verbose_name_plural = '동아리 홍보 사진(들)'

    def __str__(self):
        return self.club.name

    club = models.ForeignKey(
        Club,
        related_name='images',
        verbose_name='동아리',
    )
    image = models.FileField(
        null=False,
        upload_to='ot/',
        verbose_name='홍보 사진',
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='메인 화면에 올라갈 사진인가 (하나만 가능)',
    )
