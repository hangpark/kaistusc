from django.conf.urls import url

from apps.rule.views import (RevisionView, RevisionTitleView,
                             RevisionChapterView, RevisionArticleView,
                             RevisionDiscussionView,
                             AddDiscussionView, AddCommentView)


def url_format(path, view):
    return url(r'^((?P<rule_set>\w+)/)?{}$'.format(path), view)

urlpatterns = [
    url_format(r'(?P<target>candidate)', RevisionView.as_view()),
    url_format(r'(?P<target>current)', RevisionView.as_view()),
    url_format(r'title', RevisionTitleView.as_view()),
    url_format(r'(?P<type>preamble)', RevisionChapterView.as_view()),
    url_format(r'(?P<type>chapter)/(?P<chapter>\d+)(/(?P<sub_chapter>\d+))?',
               RevisionChapterView.as_view()),
    url_format(r'(?P<type>supplement)', RevisionChapterView.as_view()),
    url_format(r'(?P<type>article)/(?P<article>\d+)', RevisionArticleView.as_view()),
    url_format(r'(?P<type>supplement)/(?P<article>\d+)', RevisionArticleView.as_view()),
    url_format(r'discussion', RevisionDiscussionView.as_view()),

    url(r'^(?P<type>\w+)/(?P<id>\d+)/discussion/new$', AddDiscussionView.as_view()),
    url(r'^discussion/(?P<id>\d+)/comment/new$', AddCommentView.as_view()),
]
