from django.conf.urls import include, url

from apps.board.views import BoardView, PostView

urlpatterns = [
    url(r'^(?:(?P<tag>[a-z0-9]*[a-z]+[a-z0-9]*)/)?$', BoardView.as_view()),
]
