# -*- coding:utf-8 -*-

from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.views.generic import TemplateView, View

from . import settings


class LoginView(TemplateView):

    template_name = 'ksso/login.html'

    def dispatch(self, request, *args, **kwargs):
        from .classes import PortalController
        self.token = self.request.COOKIES.get('SATHTOKEN', False)
        if self.token:
            self.user = PortalController(self.token).retrieve_user()
            if self.user:
                login(request, self.user)
                self.next = self.request.COOKIES.get(
                        'REDIRECT_URL_TOKEN', settings.AUTH_REDIRECT_URL)
                response = redirect(self.next)
            else:
                response = redirect(settings.AUTH_REDIRECT_URL)
            response.delete_cookie('SATHTOKEN', '/', '.kaist.ac.kr')
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
