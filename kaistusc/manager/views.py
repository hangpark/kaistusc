from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView

from .models import Category, Service


class PermissionRequiredServiceMixin(object):
    """
    View를 요청한 유저가 대응 서비스에 대한 접속권한이 없는 경우
    PermissionDenied Exception을 발생시키는 mixin.

    PermissionDenied Exception이 발생되면 401 에러가 나오며, DEBUG 모드가
    아닐 때 template을 customizing 할 수 있다.
    """

    service_name = None

    def has_permission(self, request):
        service = Service.objects.filter(name=self.service_name).first()
        if not service:
            return False
        return service.is_accessible(request.user)

    def handle_no_permission(self):
        raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request):
            return self.handle_no_permission()
        return super(PermissionRequiredServiceMixin, self).dispatch(
            request, *args, **kwargs)


class NavigatorMixin(object):
    """
    사이트 네비게이터를 생성하는 Mixin.
    """

    service_name = None

    def get_context_data(self, **kwargs):
        kwargs['navigator'] = []
        categories = Category.objects.all()
        for category in categories:
            kwargs['navigator'].append(Service.objects.filter(
                category=category).accessible_for(self.request.user))
        return super(NavigatorMixin, self).get_context_data(**kwargs)


class BaseServiceView(PermissionRequiredServiceMixin,
        NavigatorMixin, TemplateView):
    """
    기본 서비스 view.

    본 view를 상속받아 구체적인 서비스를 구현하며,
    TemplateView를 기본 구조로 하고 있다.
    """
    pass
