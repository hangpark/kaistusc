from django.db import models
from django.contrib.auth.models import User

from .club import Club


class Freshman(models.Model):
    def __str__(self):
        return self.user.username

    user = models.OneToOneField(User, related_name='freshman')
    voted_clubs = models.ManyToManyField(Club, related_name='votes')

    sizes = (
        ('xs', 'xs'),
        ('s', 's'),
        ('m', 'm'),
        ('l', 'l'),
        ('xl', 'xl'),
    )
    tsize = models.CharField(null=False, max_length=5, choices=sizes)

    BAND_VOTE_LIMIT = 2
    NON_BAND_VOTE_LIMIT = 3

    def vote_limit_exceeded(self, is_band):
        cnt = self.voted_clubs.filter(is_band=is_band).count()

        if is_band:
            return cnt >= self.BAND_VOTE_LIMIT
        else:
            return cnt >= self.NON_BAND_VOTE_LIMIT
