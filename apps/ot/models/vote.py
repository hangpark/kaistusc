from django.db import models


class VotePolicy(models.Model):
    """
    투표 시작/종료 시간, 서비스/테스트 여부 등을 코드배포 없이 수정하도록 db에 저장
    """
    is_test = models.BooleanField()
    start = models.DateTimeField()
    end = models.DateTimeField()
