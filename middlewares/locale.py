"""
로케일 설정 미들웨어.
"""

from django.conf import settings
from django.utils import translation
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin


class SessionBasedLocaleMiddleware(MiddlewareMixin):
    """
    GET 파라미터로 전달된 ``lang`` 값의 언어로 로케일을 설정하는 미들웨어.

    한 번 전달된 ``lang`` 값은 세션에 ``language`` 이름으로 저장되어
    지속성을 유지합니다.

    https://djangosnippets.org/snippets/1948/ 의 코드를 1.10 버전에 맞게
    수정하였습니다.
    """

    def process_request(self, request):
        """
        GET 파라미터로 ``lang`` 값이 전달되거나 세션에 ``language`` 값이 설정된
        경우 해당 언어코드에 맞는 언어로 사이트를 번역하는 메서드.

        아무런 언어코드가 전달되지 않은 경우 리퀘스트를 통해 로케일을
        설정합니다. 또한, GET 파라미터로 언어코드가 전달된 경우 이를 세션에
        저장합니다.
        """
        if request.method == 'GET' and 'lang' in request.GET:
            language = request.GET['lang']
            request.session['language'] = language
        elif 'language' in request.session:
            language = request.session['language']
        else:
            language = translation.get_language_from_request(request)
        for lang in settings.LANGUAGES:
            if lang[0] == language:
                translation.activate(language)

        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        """
        번역을 완료하고 응답을 반환하는 메서드.
        """
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
