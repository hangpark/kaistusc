from django.contrib.auth import login, logout
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.views.generic import TemplateView, View

from apps.manager.views import PageView

from . import settings


class LoginView(TemplateView):

    template_name = 'ksso/login.jinja'

    def dispatch(self, request, *args, **kwargs):
        from .classes import PortalController
        self.token = self.request.COOKIES.get('SATHTOKEN', False)
        if self.token:
            self.user = PortalController(self.token).retrieve_user()
            if self.user:
                login(request, self.user)
                self.next = self.request.COOKIES.get(
                        'REDIRECT_URL_TOKEN', settings.AUTH_REDIRECT_URL)
                if self.user.portal_info.is_signed_up:
                    response = redirect(self.next)
                else:
                    response = redirect('ksso:signup')
                    response['Location'] += '?next=%s' % (self.next,)
            else:
                response = redirect(settings.AUTH_REDIRECT_URL)
            response.delete_cookie('REDIRECT_URL_TOKEN')
            response.delete_cookie('SATHTOKEN', '/', '.kaist.ac.kr')
            return response
        self.next = self.request.GET.get('next', settings.AUTH_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response.set_cookie('REDIRECT_URL_TOKEN', self.next)
        return response


class LogoutView(View):
    def dispatch(self, request, *args, **kwargs):
        self.next = self.request.GET.get('next', settings.AUTH_REDIRECT_URL)
        logout(request)
        return redirect(self.next)


class SignUpView(PageView):

    template_name = 'ksso/signup.jinja'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect_to_login(request.path)
        return super().dispatch(request, *args, **kwargs)

    def is_signed_up(self, request):
        return not (request.user.is_authenticated()
                and hasattr(request.user, 'portal_info')
                and not request.user.portal_info.is_signed_up)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_signed_up'] = self.is_signed_up(self.request)
        return context


class AgreeView(View):
    """
    유저가 정보제공에 동의하였을 때 동의처리 후 리다이렉션을 진행하는 뷰.
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            portal_info = request.user.portal_info
            portal_info.is_signed_up = True
            portal_info.save()
        except:
            pass
        return redirect(request.GET.get('next', settings.AUTH_REDIRECT_URL))
        

class DisagreeView(View):
    """
    유저가 정보제공을 거부하였을 때 로그아웃 후 계정삭제를 진행하는 뷰.

    """

    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user.portal_info.is_signed_up:
                user = request.user
                logout(request)
                user.delete()
        except:
            pass
        return redirect('main')
