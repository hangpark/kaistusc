"""
KAIST 단일인증서비스 뷰.
"""

from django.conf import settings as project_settings
from django.contrib.auth import login, logout, load_backend, SESSION_KEY, BACKEND_SESSION_KEY
from django.contrib.auth.views import redirect_to_login
from django.contrib.sessions.models import Session
from django.shortcuts import redirect
from django.views.generic import TemplateView, View

from rest_framework import views, status, response

from apps.manager.views import PageView

from . import settings
from .classes import PortalController
from .serializers import UserSerializer


class LoginView(TemplateView):
    """
    로그인 뷰.

    사용자의 쿠키에 KAIST 단일인증서비스 토큰이 존재하는 경우 이를 통해 서버와
    통신하여 사용자 로그인을 처리합니다. 존재하지 않는 경우 아직 사용자가
    로그인 정보 입력을 하지 않은 것으로 판단하여 KAIST 단일인증서비스에서
    제공하는 로그인 창으로 이동시킵니다.
    """

    template_name = 'ksso/login.jinja'

    def dispatch(self, request, *args, **kwargs):
        """
        사용자에게 토큰이 존재할 시 로그인을 처리하고 그 외엔 로그인 페이지로
        이동시키는 메서드.

        토큰이 존재하는 경우 로그인 절차를 수행합니다. 이후 쿠키에 저장된
        리다이렉션 URL로 이동시키고 토큰과 리다이렉션 정보를 쿠키에서
        삭제합니다. 토큰이 존재하지 않는 경우 GET 파라미터로 전달된 ``next``
        값을 쿠키에 저장한 후 로그인 페이지로 이동시킵니다.

        즉, 정상적인 사용자는 KAIST 단일인증서비스에서 제공하는 로그인
        페이지에서 포탈 계정정보를 입력하기 전과 후 총 두 번 본 뷰를 실행합니다.
        """
        token = request.COOKIES.get('SATHTOKEN', False)
        if token:
            return self.process_login(token)
        self.next = self.request.GET.get('next', settings.AUTH_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def process_login(self, token):
        """
        토큰값을 이용하여 사용자 정보를 가져와 로그인하는 메서드.

        토큰값이 올바르지 않아 인증 절차가 올바르게 완료되지 못한 경우 기본
        리다이렉트 URL로 이동합니다.
        """
        try:
            user = PortalController(token).retrieve_user()
        except:
            response = redirect(settings.AUTH_REDIRECT_URL)
        else:
            login(self.request, user)
            self.next = self.request.COOKIES.get(
                'REDIRECT_URL_TOKEN', settings.AUTH_REDIRECT_URL)
            if user.portal_info.is_signed_up:
                response = redirect(self.next)
            else:
                response = redirect('ksso:signup')
                response['Location'] += '?next={}'.format(self.next)
        response.delete_cookie('REDIRECT_URL_TOKEN')
        response.delete_cookie('SATHTOKEN', '/', '.kaist.ac.kr')
        return response

    def render_to_response(self, context, **response_kwargs):
        """
        리다이렉션 정보를 사용자의 쿠키에 저장하는 메서드.
        """
        response = super().render_to_response(context, **response_kwargs)
        response.set_cookie('REDIRECT_URL_TOKEN', self.next)
        return response


class LogoutView(View):
    """
    로그아웃 뷰.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        사용자 로그아웃을 진행하는 메서드.

        GET 파라미터의 ``next`` 값에 있는 주소로 리다이렉션을 진행합니다.
        """
        self.next = self.request.GET.get('next', settings.AUTH_REDIRECT_URL)
        logout(request)
        return redirect(self.next)


class SignUpView(PageView):
    """
    정보제공 동의페이지 뷰.
    """

    template_name = 'ksso/signup.jinja'

    def dispatch(self, request, *args, **kwargs):
        """
        로그인 되지 않았을 경우 로그인 페이지로 이동시키는 메서드.
        """
        if not request.user.is_authenticated():
            return redirect_to_login(request.path)
        return super().dispatch(request, *args, **kwargs)

    def is_signed_up(self, request):
        """
        사용자가 정보제공에 동의했는지 여부를 반환하는 메서드.

        KAIST 단일인증서비스를 이용하지 않은 특수계정의 경우 동의한 것으로
        간주합니다.
        """
        return not (
            request.user.is_authenticated() and
            hasattr(request.user, 'portal_info') and
            not request.user.portal_info.is_signed_up)

    def get_context_data(self, **kwargs):
        """
        사용자가 정보제공에 동의했는지 여부를 컨텍스트에 추가하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        context['is_signed_up'] = self.is_signed_up(self.request)
        return context


class AgreeView(View):
    """
    정보제공 동의처리 뷰.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        사용자가 정보제공에 동의하였을 때 :class:`PortalInfo` 인스턴스에
        정보제공 동의표시를 한 후 리다이렉션을 진행하는 메서드.
        """
        try:
            portal_info = request.user.portal_info
            portal_info.is_signed_up = True
            portal_info.save()
        except:
            pass
        return redirect(request.GET.get('next', settings.AUTH_REDIRECT_URL))


class DisagreeView(View):
    """
    정보제공 미동의처리 뷰.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        사용자가 정보제공을 거부하였을 때 로그아웃 후 계정삭제를 진행하는
        메서드.
        """
        try:
            if not request.user.portal_info.is_signed_up:
                user = request.user
                logout(request)
                user.delete()
        except:
            pass
        return redirect('main')


class UserInfoView(views.APIView):
    def get(self, request, format=None):
        if request.META['REMOTE_ADDR'] not in project_settings.ALLOWED_REMOTE_ADDRS:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        session_key = request.GET.get('session_key')

        if not session_key:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            session = Session.objects.get(session_key=session_key)

            try:
                user_id = session.get_decoded()[SESSION_KEY]
                backend_path = session.get_decoded()[BACKEND_SESSION_KEY]

            except KeyError:
                pass

            else:
                if backend_path in project_settings.AUTHENTICATION_BACKENDS:
                    backend = load_backend(backend_path)

                    return response.Response(UserSerializer(backend.get_user(user_id)).data)

        except Session.DoesNotExist:
            pass

        return response.Response(status=status.HTTP_404_NOT_FOUND)
