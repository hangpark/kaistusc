"""
게시판 URL 설정.
"""

from django.conf.urls import url

from apps.board.views import (
    BoardView,
    ProductView,ProductDeleteView,
    CommentDeleteView,CommentView,
    PostDeleteView, PostEditView, PostView, PostWriteView, PostVoteView,
    BoardBannerWriteView, BoardBannerEditView, BoardBannerDeleteView
)

url_tab = r'^(?:(?P<tab>[a-z0-9]*[a-z]+[a-z0-9]*)/)?'

urlpatterns = [
    url(url_tab + r'product/$',
        ProductView.as_view()),

    url(url_tab + r'banner/new/$',
        BoardBannerWriteView.as_view()),

    url(url_tab + r'banner/edit/$',
        BoardBannerEditView.as_view()),

    url(url_tab + r'banner/(?P<board_banner_id>[0-9]+)/delete/$',
        BoardBannerDeleteView.as_view()),

    url(url_tab + r'new/$',
        PostWriteView.as_view()),

    url(url_tab + r'$',
        BoardView.as_view()),

    url(url_tab + r'product/(?P<product_id>[0-9]+)/delete/$',
        ProductDeleteView.as_view()),

    url(url_tab + r'(?P<post>[0-9]+)/$',
        PostView.as_view()),

    url(url_tab + r'(?P<post>[0-9]+)/edit/$',
        PostEditView.as_view()),

    url(url_tab + r'(?P<post>[0-9]+)/delete/$',
        PostDeleteView.as_view()),

    url(url_tab + r'(?P<post>[0-9]+)/comment/$',
        CommentView.as_view()),

    url(url_tab + r'(?P<post>[0-9]+)/comment/(?P<comment>[0-9]+)/delete/$',
        CommentDeleteView.as_view()),

    url(url_tab + r'(?P<post>[0-9]+)/vote/(?P<mode>up)/$',
        PostVoteView.as_view()),

    url(url_tab + r'(?P<post>[0-9]+)/vote/(?P<mode>down)/$',
        PostVoteView.as_view()),
]
