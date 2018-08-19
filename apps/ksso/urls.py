"""
KAIST 단일인증서비스 URL 설정.
"""

from django.conf.urls import url

from .views import AgreeView, DisagreeView, LoginView, LogoutView, SignUpView, UserInfoView

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^signup/$', SignUpView.as_view(), name='signup'),
    url(r'^signup/agree/$', AgreeView.as_view()),
    url(r'^signup/disagree/$', DisagreeView.as_view()),

    url(r'^info/$', UserInfoView.as_view()),
]
