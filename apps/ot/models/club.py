from django.db import models


class Club(models.Model):
    """
    동아리 정보
    """
    def __str__(self):
        return str(self.name)

    name = models.CharField(max_length=63)
    pages = models.TextField()
    intro = models.TextField()
    ad = models.TextField()
    is_band = models.BooleanField(default=False)

    video_url1 = models.CharField(max_length=63)
    video_url2 = models.CharField(max_length=63)


class Image(models.Model):
    """
    동아리 홍보 사진
    """
    def __str__(self):
        return self.club.name

    club = models.ForeignKey(Club, related_name='images')
    image = models.FileField(null=False, upload_to='ot/')
