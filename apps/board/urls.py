"""
게시판 URL 설정.
"""

from django.conf.urls import url

from apps.board.views import (BoardView, CommentDeleteView, CommentWriteView,
                              PostDeleteView, PostEditView, PostView,
                              PostVoteView, PostWriteView, PdfLatestView)

url_tag = r'^(?:(?P<tag>[a-z0-9]*[a-z]+[a-z0-9]*)/)?'

urlpatterns = [
    url(r'^new/$',
        PostWriteView.as_view()),

    url(r'^latest/$',
        PdfLatestView.as_view()),

    url(url_tag + r'$',
        BoardView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/$',
        PostView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/edit/$',
        PostEditView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/delete/$',
        PostDeleteView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/comment/$',
        CommentWriteView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/comment/(?P<comment>[0-9]+)/delete/$',
        CommentDeleteView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/vote/(?P<mode>up)/$',
        PostVoteView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/vote/(?P<mode>down)/$',
        PostVoteView.as_view()),
]
