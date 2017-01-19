# -*- coding:utf-8 -*-

from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.views.generic import TemplateView, View

from . import settings
from apps.manager.views import NavigatorMixin


class LoginView(TemplateView):

    template_name = 'ksso/login.html'

    def dispatch(self, request, *args, **kwargs):
        from .classes import PortalController
        self.token = self.request.COOKIES.get('SATHTOKEN', False)
        if self.token:
            self.user = PortalController(self.token).retrieve_user()
            response.delete_cookie('SATHTOKEN', '/', '.kaist.ac.kr')
            if self.user:
                login(request, self.user)
                self.next = self.request.COOKIES.get(
                        'REDIRECT_URL_TOKEN', settings.AUTH_REDIRECT_URL)
                if not self.user.portal_info.is_signed_up:
                    return redirect('ksso:signup')
                response = redirect(self.next)
            else:
                response = redirect(settings.AUTH_REDIRECT_URL)
            response.delete_cookie('REDIRECT_URL_TOKEN')
            return response
        self.next = self.request.GET.get('next', settings.AUTH_REDIRECT_URL)
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        response = super(LoginView, self).render_to_response(
                context, **response_kwargs)
        response.set_cookie('REDIRECT_URL_TOKEN', self.next)
        return response


class LogoutView(View):
    def dispatch(self, request, *args, **kwargs):
        self.next = self.request.GET.get('next', settings.AUTH_REDIRECT_URL)
        logout(request)
        return redirect(self.next)


class SignUpView(NavigatorMixin, TemplateView):

    template_name = 'ksso/signup.jinja'


class AgreeView(View):
    """
    유저가 정보제공에 동의하였을 때 동의처리 후 리다이렉션을 진행하는 뷰.
    """

    def dispatch(self, request, *args, **kwargs):
        self.next = self.request.COOKIES.get(
            'REDIRECT_URL_TOKEN', settings.AUTH_REDIRECT_URL)
        response = redirect(self.next)
        response.delete_cookie('REDIRECT_URL_TOKEN')
        try:
            portal_info = request.user.portal_info
            portal_info.is_signed_up = True
            portal_info.save()
        except:
            pass
        return response
        

class DisagreeView(View):
    """
    유저가 정보제공을 거부하였을 때 로그아웃 후 계정삭제를 진행하는 뷰.

    """

    def dispatch(self, request, *args, **kwargs):
        response = redirect('main')
        response.delete_cookie('REDIRECT_URL_TOKEN')
        try:
            if not request.user.portal_info.is_signed_up:
                user = request.user
                logout(request)
                user.delete()
        except:
            pass
        return response
