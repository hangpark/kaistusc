from django.conf.urls import url

from .views.main import MainView
from .views.club import ClubDetailView, ClubListView
from .views.user import TSizeView, ResultView

urlpatterns = [
    url(r'^$', MainView.as_view(), name='main'),
    url(r'^result/$', ResultView.as_view()),
    url(r'^tshirt/$', TSizeView.as_view(), name='t_size'),
    url(r'^club/$', ClubListView.as_view(), name='club_list'),
    url(r'^club/(?P<pk>\d+)/$', ClubDetailView.as_view(), name='club_detail'),
]
