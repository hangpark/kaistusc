from django.utils import timezone
from .models.vote import VotePolicy


def vote_available(user):
    if is_vote_period():
        return is_freshman(user)
    else:
        return is_tester(user)


def is_freshman(user):
    if not user.is_authenticated or not hasattr(user, 'portal_info'):
        return False

    portal_info = user.portal_info
    return portal_info.ku_std_no[:4] == "2018" and portal_info.ku_acad_prog == "학사"


def is_tester(user):
    if not user.is_authenticated or not hasattr(user, 'portal_info'):
        return False

    return user.portal_info.ku_std_no in ("20140191", "20170742", "20170286", "20170463", "20150305", "20170337", "20170656",)


def is_vote_period():
    if VotePolicy.objects.count() == 0:
        return False
    vote_policy = VotePolicy.objects.all()[0]
    time_now = timezone.now()

    return vote_policy.start <= time_now <= vote_policy.end
