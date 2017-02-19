from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.http import Http404

default_app_config = 'apps.manager.apps.ManagerConfig'


class Custom404(Http404):
    """
    View에서 404 에러를 발생시키는 커스텀 에러.

    인자로 문자열을 보내면 에러페이지에 표시됩니다.
    """
    pass


class Custom500(Exception):
    """
    View에서 500 에러를 발생시키는 커스텀 에러.

    인자로 문자열을 보내면 에러페이지에 표시됩니다.
    """
    pass


class Custom403(PermissionDenied):
    """
    View에서 403 에러를 발생시키는 커스텀 에러.

    인자로 문자열을 보내면 에러페이지에 표시됩니다.
    """
    pass


class Custom400(SuspiciousOperation):
    """
    View에서 400 에러를 발생시키는 커스텀 에러.

    인자로 문자열을 보내면 에러페이지에 표시됩니다.
    """
    pass
