from django.utils import timezone
from .models.vote import VotePolicy


def vote_available(user):
    if is_vote_period():
        return is_freshman(user)
    else:
        return is_tester(user)


def is_freshman(user):
    if not user.is_authenticated:
        return False

    portal_info = user.portal_info
    return portal_info.ku_std_no[:4] == "2017" and portal_info.ku_acad_prog == "학사"


def is_tester(user):
    return user.is_authenticated and user.username in ['ot', 'namsan']


def is_vote_period():
    vote_policy = VotePolicy.objects.all()[0]
    time_now = timezone.now()

    return vote_policy.start <= time_now <= vote_policy.end
