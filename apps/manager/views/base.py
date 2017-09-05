"""
사이트 관리도구 기본 뷰.
"""

import os

from django.contrib.auth.mixins import AccessMixin
from django.http import Http404
from django.views.generic import TemplateView

from apps.ksso.mixins import SignUpRequiredMixin
from apps.manager.constants import *
from apps.manager.models import Category, Service


class PermissionContextMixin(object):
    """
    템플릿에서 서비스 권한상수를 사용할 수 있도록 컨텍스트에 넘기는 믹스인.

    :meth:`get_context_data` 는 GET 요청을 처리할 때 CBV에서 자주 사용되는
    메서드입니다. 이것이 호출될 때 7가지 기본 서비스 권한들을 컨텍스트에
    저장하는 믹스인입니다.
    """

    def get_permission_context(self, context):
        """
        7가지 기본 서비스 권한을 컨텍스트에 추가하는 메서드.
        """
        context['PERM_NONE'] = PERM_NONE
        context['PERM_ACCESS'] = PERM_ACCESS
        context['PERM_READ'] = PERM_READ
        context['PERM_COMMENT'] = PERM_COMMENT
        context['PERM_WRITE'] = PERM_WRITE
        context['PERM_EDIT'] = PERM_EDIT
        context['PERM_DELETE'] = PERM_DELETE
        return context

    def get_context_data(self, **kwargs):
        """
        컨텍스트에 들어갈 데이터를 설정하는 메서드.

        :meth:`super` 메서드를 통해 컨텍스트 데이터를 얻어온 후
        :meth:`get_permission_context` 메서드를 호출하여 기본 서비스 권한을
        추가합니다.
        """
        context = super().get_context_data(**kwargs)
        return self.get_permission_context(context)


class PermissionRequiredServiceMixin(AccessMixin):
    """
    뷰를 요청한 사용자가 서비스에 대한 접속권한이 없는 경우 403 에러를
    발생시키는 믹스인.

    서비스가 존재하는 경우 전역변수 `service` 에 서비스 객체를 저장합니다. 이후
    해당 서비스에 대해 사용자의 이용권한을 테스트하고 권한이 없을 경우 403
    에러를 발생시킵니다. 서비스가 존재하지 않는 경우 404 에러를 발생시킵니다.
    403 에러와 404 에러가 발생하면 핸들러를 통해 커스텀 에러페이지로 이동시킬 수
    있습니다.

    이용권한은 전역변수 `required_exception` 에 저장되며, 기본 값은 접근권한으로
    설정되어 있습니다.
    """

    service_name = None
    required_permission = PERM_ACCESS
    raise_exception = True

    def get_service(self, request, *args, **kwargs):
        """
        사용자 요청으로부터 서비스를 얻어내는 매서드.

        기본적으로 사용자가 요청한 URL에 해당하는 정규표현식 패턴으로부터 전달된
        `url` 파라미터가 있을 경우 이와 일치하는 URL을 갖는 서비스를 반환합니다.
        `url` 파라미터가 전달되지 않은 경우 전역변수 `service_name` 와 같은
        이름을 갖는 서비스를 반환합니다. 서비스명은 한국어 이름으로 갈음합니다.

        위의 두 방식 외 기타 방식으로 서비스가 특정되는 경우 본 메서드를 적절히
        오버라이드 하여 로직을 구현하실 수 있습니다.
        """
        if (kwargs.get('url', None)):
            url = os.path.join('/', kwargs['url'])
            return Service.objects.filter(url=url).first()
        return Service.objects.filter(name_ko=self.service_name).first()

    def has_permission(self, request, *args, **kwargs):
        """
        사용자가 서비스 이용권한이 있는지 여부를 반환하는 메서드.

        :meth:`get_service` 메서드를 통한 서비스 얻어내기가 실패한 경우 404
        에러가 발생합니다. 제대로 서비스를 얻어낸 경우 이를 전역변수 `service`에
        저장합니다.
        """
        service = self.get_service(request, *args, **kwargs)
        if not service:
            raise Http404
        self.service = service
        return service.is_permitted(request.user, self.required_permission)

    def dispatch(self, request, *args, **kwargs):
        """
        권한이 없는 사용자의 요청을 사전차단하는 메서드.
        """
        if not self.has_permission(request, *args, **kwargs):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class NavigatorMixin(object):
    """
    사이트 네비게이터를 생성하여 컨텍스트에 넘기는 믹스인.

    :meth:`get_context_data` 는 GET 요청을 처리할 때 CBV에서 자주 사용되는
    메서드입니다. 이것이 호출될 때 카테고리와 서비스의 계층구조를 컨텍스트에
    저장하는 믹스인입니다.
    """

    def get_context_data(self, **kwargs):
        """
        컨텍스트에 들어갈 데이터를 설정하는 메서드.

        :meth:`super` 메서드를 통해 컨텍스트 데이터를 얻어온 후 카테고리와
        각각의 카테고리 하위의 사용자 접근 가능 서비스를 얻어 사이트 네비게이터
        데이터를 컨텍스트에 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        context['navigator'] = []
        categories = Category.objects.filter(is_open=True)
        for category in categories:
            context['navigator'].append({
                'category': category,
                'services': Service.objects.filter(
                    category=category).accessible_for(self.request.user),
            })
        return context


class PageView(NavigatorMixin, TemplateView):
    """
    페이지 뷰.

    사용자 권한관리가 필요하지 않는 서비스나 고정 페이지를 출력하는 뷰입니다.
    단순히 `TemplateView` 에 네비게이터를 설정한 것에 지나지 않습니다. 이는
    사이트 기본 레이아웃을 사용하기 위함입니다.

    각각의 페이지 역시 서비스가 될 수 있습니다. 서비스는 어떤 뷰를 사용하냐에
    관계있는 개념이 아니며, `Service` 모델의 객체로 등록되어 데이터베이스에
    저장되면 서비스가 됩니다. 따라서 페이지 뷰를 사용하는 컨텐츠 역시 서비스로
    등록할 수 있습니다.
    """

    pass


class ServiceView(
        SignUpRequiredMixin, PermissionContextMixin,
        PermissionRequiredServiceMixin, PageView):
    """
    기본 서비스 뷰.

    서비스의 각 뷰는 본 뷰를 상속하여 구현합니다. 권한에 따른 이용제한 기능과
    각종 필요한 컨텍스트가 여러 믹스인들에 의해 이미 구현되어 있습니다.

    전역변수 `service_name` 에서 대응되는 서비스명을 지정해줄 수 있습니다.
    URL 패턴 정규표현식에 `url` 파라미터가 존재하지 않는 경우 서비스명을 이곳에
    밝혀주세요.

    전역변수 `required_permission` 에서 뷰의 접근에 필요한 최소 서비스 권한을
    설정할 수 있습니다. 이곳에 설정된 권한이 없는 사용자는 403 에러페이지로
    이동 처리됩니다. 더욱 복잡한 권한처리는 :meth:`has_permission` 메서드를
    오버라이드하여 구현할 수 있습니다.
    """

    def get_context_data(self, **kwargs):
        """
        컨텍스트에 서비스 객체를 전달하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        return context
