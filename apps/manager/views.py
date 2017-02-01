from django.contrib.auth.mixins import AccessMixin
from django.http import Http404
from django.views.generic import TemplateView
import os

from apps.ksso.mixins import SignUpRequiredMixin
from apps.board.models import Board

from .models import Category, Service
from .permissions import *


class PermissionContextMixin(object):
    """
    템플릿에서 퍼미션 변수들을 사용할 수 있도록 컨텍스트에 이를 넘기는 mixin.
    """

    def get_permission_context(self, context):
        context['PERMISSION_NONE'] = PERMISSION_NONE
        context['PERMISSION_ACCESSIBLE'] = PERMISSION_ACCESSIBLE
        context['PERMISSION_READABLE'] = PERMISSION_READABLE
        context['PERMISSION_COMMENTABLE'] = PERMISSION_COMMENTABLE
        context['PERMISSION_WRITABLE'] = PERMISSION_WRITABLE
        context['PERMISSION_EDITABLE'] = PERMISSION_EDITABLE
        context['PERMISSION_DELETABLE'] = PERMISSION_DELETABLE
        return context

    def get_context_data(self, **kwargs):
        context = super(PermissionContextMixin, self).get_context_data(**kwargs)
        return self.get_permission_context(context)


class PermissionRequiredServiceMixin(AccessMixin):
    """
    View를 요청한 유저가 대응 서비스에 대한 접속권한이 없는 경우
    403 에러를 발생시키는 mixin.

    서비스가 존재하지 않는 경우 404 에러를 발생시킨다. 403 에러와 404 에러에
    대해서 DEBUG 모드가 아닐 때 template을 customizing 할 수 있다.
    """

    service_name = None
    required_permission = PERMISSION_ACCESSIBLE
    raise_exception = True

    def get_service(self, request, *args, **kwargs):
        """
        User request로부터 서비스를 얻어내는 함수.

        기본적으로 요청 URL 정규표현식에 담긴 url 파라미터의 값과 서비스의
        url을 비교하여 서비스를 특정한다. url 파라미터가 전달되지 않은 경우
        service_name을 통해 서비스를 얻는다.

        기타 방식으로 서비스가 특정되는 경우와 같은 특수상황에서는 본 함수를
        커스터마이징 하여 적절한 로직을 구현할 수 있다.
        """
        if (kwargs.get('url', None)):
            url = os.path.join('/', kwargs['url'])
            return Service.objects.filter(url=url).first()
        return Service.objects.filter(name_ko=self.service_name).first()

    def has_permission(self, request, *args, **kwargs):
        service = self.get_service(request, *args, **kwargs)
        if not service:
            raise Http404
        self.service = service
        return service.is_permitted(request.user, self.required_permission)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request, *args, **kwargs):
            return self.handle_no_permission()
        return super(PermissionRequiredServiceMixin, self).dispatch(
            request, *args, **kwargs)


class NavigatorMixin(object):
    """
    사이트 네비게이터를 생성하는 Mixin.
    """

    def get_context_data(self, **kwargs):
        context = super(NavigatorMixin, self).get_context_data(**kwargs)
        context['navigator'] = []
        categories = Category.objects.all()
        for category in categories:
            context['navigator'].append({
                'category': category,
                'services': Service.objects.filter(
                    category=category).accessible_for(self.request.user),
            })
        return context


class PageView(NavigatorMixin, TemplateView):
    """
    페이지 view.
    """

    pass


class BaseServiceView(PermissionContextMixin, PermissionRequiredServiceMixin,
        PageView):
    """
    기본 서비스 view.

    본 view를 상속받아 구체적인 서비스를 구현하며,
    TemplateView를 기본 구조로 하고 있다.
    """

    def get_context_data(self, **kwargs):
        context = super(BaseServiceView, self).get_context_data(**kwargs)
        context['service'] = self.service
        return context


class MainPageView(PageView):
    """
    메인 페이지 view.

    유저가 접근 가능한 공개게시판의 글을 확인한다.
    """

    template_name = 'manager/main.jinja'

    def get_context_data(self, **kwargs):
        context = super(MainPageView, self).get_context_data(**kwargs)
        context['boards'] = Board.objects.accessible_for(
            self.request.user).filter(is_main=True)
        return context


class ErrorView(PageView):
    """
    에러 뷰
    """

    status_code = 200

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['status'] = self.status_code
        return super(ErrorView, self).render_to_response(context, **response_kwargs)
