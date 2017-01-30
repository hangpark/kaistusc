"""kaistusc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from apps.board.views import BoardView
from apps.manager.views import BaseServiceView, MainPageView

urlpatterns = [
    # Main page
    url(r'^$', MainPageView.as_view(), name='main'),

    # Basic app redirections
    url(r'^admin/', admin.site.urls),
    url(r'^user/', include('apps.ksso.urls', namespace='ksso')),

    # Service redirections
    url(r'^(?P<url>board/[a-z0-9]*[a-z]+[a-z0-9]*)/', include('apps.board.urls')),

    # Custom static pages
]
