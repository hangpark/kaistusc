from django.conf import settings

from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin

class SessionBasedLocaleMiddleware(MiddlewareMixin):
    """
    GET parameter로 lang 값이 전달되면 해당 언어로 번역하는 middleware.

    한 번 전달된 lang 값은 session에 language 이름으로 저장되어
    지속성을 유지한다.

    https://djangosnippets.org/snippets/1948/ 의 코드를 1.10 버전에 맞게
    수정하였다.
    """

    def process_request(self, request):
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
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
