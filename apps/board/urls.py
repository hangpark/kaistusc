"""
게시판 URL 설정.
"""

from django.conf.urls import url

from apps.board.views import (BoardView, CommentDeleteView,CommentWriteWithFileView,CommentWriteView,DebateWriteView,DebateView, DebateEditView,PostDeleteView, PostEditView, PostView,PostWriteView,PostVoteView)

url_tag = r'^(?:(?P<tag>[a-z0-9]*[a-z]+[a-z0-9]*)/)?'

urlpatterns = [
    url(r'^new/$',
        PostWriteView.as_view()),

    url(r'^new_debate/$',
        DebateWriteView.as_view()),

    url(url_tag + r'$',
        BoardView.as_view()),

    url(url_tag + r'^debate/(?P<post>[0-9]+)/$',
        DebateView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/$',
        PostView.as_view()), 

    url(url_tag + r'^debate/(?P<post>[0-9]+)/edit/$',
        DebateEditView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/edit/$',
        PostEditView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/delete/$',
        PostDeleteView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/commentAttached/$',
        CommentWriteWithFileView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/comment/$',
        CommentWriteView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/comment/(?P<comment>[0-9]+)/delete/$',
        CommentDeleteView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/vote/(?P<mode>up)/$',
        PostVoteView.as_view()),

    url(url_tag + r'(?P<post>[0-9]+)/vote/(?P<mode>down)/$',
        PostVoteView.as_view()),
]
