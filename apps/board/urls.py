from django.conf.urls import include, url

from apps.board.views import BoardView, PostView, PostWriteView, PostEditView, PostDeleteView

urlpatterns = [
    url(r'^new/$',
        PostWriteView.as_view()),

    url(r'^(?:(?P<tag>[a-z0-9]*[a-z]+[a-z0-9]*)/)?$',
        BoardView.as_view()),

    url(r'^(?:(?P<tag>[a-z0-9]*[a-z]+[a-z0-9]*)/)?(?P<post>[0-9]+)/$',
        PostView.as_view()),

    url(r'^(?:(?P<tag>[a-z0-9]*[a-z]+[a-z0-9]*)/)?(?P<post>[0-9]+)/edit/$',
        PostEditView.as_view()),

    url(r'^(?:(?P<tag>[a-z0-9]*[a-z]+[a-z0-9]*)/)?(?P<post>[0-9]+)/delete/$',
        PostDeleteView.as_view()),
]
