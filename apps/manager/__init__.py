"""
사이트 관리 도구.

사이트 내 서비스를 정의하고 관리하기 위한 프로젝트 기본 제공 app 입니다.
"""

from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.http import Http404

default_app_config = 'apps.manager.apps.ManagerConfig'


class Custom404(Http404):
    """
    뷰에서 404 에러를 발생시키는 커스텀 에러.

    사용자가 요청한 페이지가 존재하지 않는 경우에 사용합니다. 에러를 발생할 시
    커스텀 에러페이지가 핸들러에 의해 보여지게 됩니다. 인자로 문자열을 보내면
    에러페이지 기본 내용 대신 표시됩니다.
    """

    pass


class Custom500(Exception):
    """
    뷰에서 500 에러를 발생시키는 커스텀 에러.

    서버 내부에서 오류가 일어난 경우에 사용합니다. 에러를 발생할 시
    커스텀 에러페이지가 핸들러에 의해 보여지게 됩니다. 인자로 문자열을 보내면
    에러페이지 기본 내용 대신 표시됩니다.
    """

    pass


class Custom403(PermissionDenied):
    """
    뷰에서 403 에러를 발생시키는 커스텀 에러.

    사용자가 접근권한이 없는 페이지에 접근한 경우에 사용합니다. 에러를 발생할 시
    커스텀 에러페이지가 핸들러에 의해 보여지게 됩니다. 인자로 문자열을 보내면
    에러페이지 기본 내용 대신 표시됩니다.
    """

    pass


class Custom400(SuspiciousOperation):
    """
    뷰에서 400 에러를 발생시키는 커스텀 에러.

    사용자의 요청에 오류가 있는 경우에 사용합니다. 에러를 발생할 시
    커스텀 에러페이지가 핸들러에 의해 보여지게 됩니다. 인자로 문자열을 보내면
    에러페이지 기본 내용 대신 표시됩니다.
    """

    pass
