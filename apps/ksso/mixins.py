from django.shortcuts import redirect


class SignUpRequiredMixin(object):
    """
    KAIST Single Auth Service 3.0으로 최초 로그인한 유저가 정보제공에
    동의하지 않았을 때 동의페이지로 redirection 하는 mixin.
    """

    def dispatch(self, request, *args, **kwargs):
        if (request.user.is_authenticated()
                and hasattr(request.user, 'portal_info')
                and not request.user.portal_info.is_signed_up):
            response = redirect('ksso:signup')
            response['Location'] += '?next=%s' % (request.path,)
            return response
        return super(SignUpRequiredMixin, self).dispatch(request, *args, **kwargs)
