"""
KAIST 단일인증서비스 믹스인.
"""

from django.shortcuts import redirect


class SignUpRequiredMixin(object):
    """
    정보제공 동의를 하지 않은 사용자를 동의페이지로 리다이렉션 시키는 믹스인.

    KAIST 단일인증서비스를 이용하여 최초 로그인한 유저가 정보제공에 동의하지
    않고 이후 다른 서비스에 접근을 시도할 때 동의페이지로 리다이렉션 하는
    믹스인입니다. :meth:`dispatch` 로 구현하여 HTTP 메서드에 관계 없이 직접적인
    뷰 로직이 실행되지 않도록 할 수 있습니다.

    효과적으로 사용하기 위해서는 구현하는 뷰에 상속 처리할 때 MRO를 높게
    설정하는 것이 필요합니다.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        정보제공 동의를 하지 않은 경우 동의페이지로 리다이렉션 시키는 메서드.
        """

        if (request.user.is_authenticated()
                and hasattr(request.user, 'portal_info')
                and not request.user.portal_info.is_signed_up):
            response = redirect('ksso:signup')
            response['Location'] += '?next=%s' % (request.path,)
            return response
        return super().dispatch(request, *args, **kwargs)
