Django
===============================================

Django 프로젝트는 최상위 폴더 안의 :file:`manage.py` 파일과 :file:`kaistusc/` 내부의 설정파일들, 그리고 :file:`apps/` 내부의 세 개의 앱과 :file:`middlewares/` 내부의 한 개의 미들웨어로 구성되어 있습니다.

본 프로젝트에서는 i18n을 위해 django-modeltranslation_ 을 이용하여 사용자 작성 컨텐츠가 유동적으로 번역될 수 있도록 하였습니다.
또한, 템플릿은 `Jinja 2`_ 엔진을 사용하였으며 이는 django-jinja_ 라이브러리를 통해 지원되고 있습니다. 다만,
내장 템플릿 엔진 역시 사용이 가능하며, ``*.jinja`` 파일은 ``django-jinja`` 로, ``*.html`` 파일은 내장 템플릿 엔진으로 처리됩니다.
이 외 자세한 사항은 각 링크를 참고하시길 바랍니다.
아래에서는 본 프로젝트의 요구사항과 각각의 앱, 미들웨어에 대해 살펴보도록 하겠습니다.


프로젝트 요구사항
-----------------

kaistusc django 프로젝트는 일반적인 django 프로젝트에 비해 몇 가지 강력한 요구사항이 존재합니다.


국제화/지역화
~~~~~~~~~~~~~

국제학생의 참여를 보장하기 위하여 모든 문자열은 :program:`gettext` 를 통해 번역 될 수 있도록 처리합니다.
기본 문자열은 한국어로 설정합니다.
예를 들어 아래는 일반적인 문자열 사용입니다.

.. code-block:: python3

    from django.db import models
    
    class Category(models.Model):
        name = models.CharField("카테고리명", max_length=32, unique=True)

위의 예시에서 *"카테고리명"* 은 ``name`` 의 ``verbose_name`` 으로, 어드민 페이지나 폼 등에서 나타나는 문자열입니다.
이를 국제화하는 방법은 아래와 같습니다.

.. code-block:: python3

    from django.db import models
    from django.utils.translation import ugettext_lazy as _

    class Category(models.Model):
        name = models.CharField(_("카테고리명"), max_length=32, unique=True)

이후 :program:`manage.py` 의 `makemessages` 명령어를 통해 ``*.po`` 파일을 생성하고 이에 대한 지역화를 수행한 후 `compilemessages` 명령어로 번역을 완료합니다.
이 때, 최소한 **영어** 번역은 완료하는 것이 본 프로젝트의 요구사항입니다.

또한, 게시글 등 사용자 입력 데이터의 경우 :program:`django-modeltranslation` 을 이용하여 영어로 번역할 수 있는 방법을 제공해야 합니다.
위에서 언급했듯이, 자세한 사항은 django-modeltranslation_ 문서를 참고하시길 바랍니다.
*(새로운 DB 테이블을 사용하는 서비스를 생성하실 때 확인하시는 것이 좋을 것입니다.)*


코멘트
~~~~~~

각 모듈과 클래스 마다 docstring을 작성하여 코드를 읽는 사람으로 하여금 그 역할을 분명히 알 수 있도록 해야 합니다.
또한, 모델 필드의 경우 ``verbose_name`` 을 필수적으로 명시하여야 하며, ``help_text`` 작성 역시 권장합니다.
모델 클래스의 경우 메타 클래스에 ``verbose_name`` 과 ``verbose_name_plural`` 를 적어야 합니다.


앱 디렉토리
~~~~~~~~~~~

새로운 앱을 생성할 때 반드시 :file:`apps/` 내부에 위치하도록 합니다.
여러 앱이 공통될 경우 :file:`apps/` 의 하위 디렉토리로 묶는 것은 허용합니다.
외부 django 라이브러리의 경우에는 당연히 해당되지 않는 내용입니다.


apps.manager (사이트 관리도구)
------------------------------

- :file:`apps/manager/`

총학생회 사이트는 기본적으로 여러가지 *서비스* 들의 집합으로 정의됩니다.
또한, 유사한 서비스들의 모임을 *카테고리* 로 두고 있습니다.
즉, 간단히 생각하면 사이트맵에서 최상위 분류가 카테고리, 그 다음 분류가 서비스라고 생각하시면 되겠습니다.

:dfn:`Manager` 앱은 요약하자면 사이트 내 서비스를 정의하고 관리하는, 사이트 관리 앱입니다.
:file:`models.py` 에는 ``Category`` 와 ``Service`` 모델이 정의되어 있습니다.
각 필드에 대한 설명은 ``verbose_name`` 에 담겨 있습니다.


서비스 권한
~~~~~~~~~~~

:dfn:`Manager` 앱이 필요한 가장 큰 이유는 **권한 관리** 때문입니다.
기본적으로 kaistusc 프로젝트는 각 서비스에 대한 권한을 아래 7가지 중 하나로 나타냅니다. (:file:`apps.manager.constants` 에 위치)

- 권한없음
- 접근권한
- 읽기권한
- 댓글권한
- 쓰기권한
- 수정권한
- 삭제권한

게시판을 예시로 들면 쉽게 이해가 가는 권한 계층이지만, 모든 서비스가 게시판과 동일한 활동 층위로 나뉠 수 있는 것은 아닙니다.
이 경우 각 권한의 위상과 비슷한 수준의 층위로 설정하는 것이 바람직할 것입니다.
대부분의 경우 위의 권한 목록 전부가 필요하지 않을 수 있습니다.
이 경우 필요한 권한들을 적절히 골라 사용하시면 됩니다.

권한은 ``GroupServicePermission`` 모델에 의해 관리됩니다.
각 서비스와 django가 기본으로 제공하는 그룹 기능 사이에 특정한 권한을 부여할 수 있습니다.
사용자가 여러 그룹에 속해있고 각 그룹이 특정 서비스에 서로 다른 권한을 지닌다면, 그 사용자는 해당 서비스에 대하여 각 그룹의 권한들 중 최고로 높은 권한을 갖게 됩니다.

특히, 서비스 모델 내의 ``max_permission_anon`` 과 ``max_permission_auth`` 를 이용하여 각각 비로그인 사용자, 로그인 사용자의 최대 권한을 설정할 수 있습니다.
이 경우 특정 사용자의 권한은 위의 최고 높은 그룹 권한과 이 필드의 값들을 비교하여 산출됩니다.
또한, ``is_closed`` 가 ``True`` 로 설정된 경우, 기존에 갖고 있던 권한에 상관 없이 관리자를 제외한 사용자는 *권한없음* 상태가 됩니다.

권한여부를 확인하는 로직은 ``is_permitted`` 메소드에 구현되어 있으며, 아래와 같이 커스텀 매니저(``ServiceManager``)와 쿼리셋 (``ServiceQueryset``)을 통해 특정 유저가 접근가능한 서비스를 뽑아낼 수 있습니다.

.. code-block:: python3

    from apps.manager.models import Service

    # In view
    services = Service.objects.filter(
        category__name="카테고리").accessible_for(request.user)


서비스 뷰
~~~~~~~~~

각 서비스는 기본적으로 ``apps.manager.views.base.ServiceView`` 를 상속받아 구현합니다.
이는 몇 가지 믹스인과 ``TemplateView`` 로 이루어져 있는 뷰입니다.
이 중 ``PermissionRequiredServiceMixin`` 은 권한이 없는 사용자가 서비스에 접근할 때 403 에러를 발생시킵니다.
기본으로는 *접근권한* 이 있는지 여부를 따지지만, ``required_permission`` 을 설정하여 다른 권한이 있을 것을 요구할 수 있습니다.

따라서 ``ServiceView`` 를 상속하여 커스텀 서비스(예를 들어 ``CustomServiceView``)를 만들고, 해당 서비스 내부의 여러 뷰는 ``CustomServiceView`` 를 상속하고 ``required_permission`` 을 조정하는 식으로 쉽게 구현할 수 있습니다.
자세한 응용 예시는 ``apps.board.views`` 를 참고하세요.

``NavigatorMixin`` 은 카테고리와 하위 접근 가능 서비스들의 계층 목록을 얻어 사이트 네비게이터를 생성합니다.
사이트 기본 레이아웃에 존재하는 네비게이션바 등을 구현하는 데에 쓰입니다.
이 믹스인과 ``TemplateView`` 를 합친 ``PageView`` 는 권한이 필요하지 않는 정적 서비스나 정적 페이지 등을 구현하는 데 요긴하게 쓰입니다.
활용 예시는 ``apps.manager.views.statics`` 를 참고하세요.


커스텀 에러
~~~~~~~~~~~

기본적으로 django는 404, 500, 403, 400 에러에 대해 이벤트 핸들러를 제공합니다.
이를 활용하면 사이트에서 에러 페이지를 커스터마이징 할 수 있습니다.
본 사이트에서도 커스텀 에러 페이지를 제공하고 있습니다.
각 종류의 에러마다 에러 문구가 다릅니다.
이를 테면, 404 에러의 경우 제목은 *'페이지가 존재하지 않습니다.'*, 내용은 *'클릭하신 링크가 잘못되었거나 페이지가 제거되었습니다.'* 로 구성된 에러 페이지가 나타납니다.

커스텀 에러는 각각의 상황에 맞는 에러 내용을 에러 페이지에 띄울 수 있도록 해줍니다.
``Custom404``, ``Custom500``, ``Custom403``, ``Custom400`` 에러 클래스가 ``apps.manager`` 에 정의되어 있습니다.
이를 이용하여 아래 예시와 같이 사용하시면 인자로 넘겨준 내용이 에러 페이지에 뜨게 됩니다.

.. code-block:: python3

    from django.utils.translation import ugettext_lazy as _

    from apps.manager import Custom404

    raise Custom404(_("존재하지 않는 게시글입니다."))


템플릿
~~~~~~

:dfn:`Manager` 앱은 사이트 기본 레이아웃을 정의한 템플릿을 제공합니다.
:file:`templates/manager/base.jinja` 는 기본 HTML 파일 구조를 정의합니다.
모바일 용 사이드 네비게이션과 헤더, 푸터는 각각 같은 디렉토리 내의 :file:`side_nav.jinja`, :file:`header.jinja`, :file:`footer.jinja` 에 기술되어 있습니다.

이 베이스 레이아웃을 토대로 서비스 기본 레이아웃을 설정한 :file:`app_base.jinja` 역시 마련되어 있습니다.
이는 카테고리명과 데스크탑 용 사이드 네비게이션을 출력하며 서비스 컨텐츠가 출력될 영역을 ``{% block content %}{% endblock %}`` 으로 잡습니다.
따라서, 새롭게 웹디자인을 하지 않고 기존 레이아웃을 사용하여 제작할 서비스의 경우 레이아웃 걱정 없이 서비스 컨텐츠만 작성하시면 됩니다.
또한, :file:`base.jinja` 에서 정의된 :dfn:`stylesheet` 블록과 :dfn:`javascript` 블록을 활용하여 추가적인 페이지 구성요소를 쉽게 로드할 수 있습니다.
아래는 예시입니다.

.. code-block:: html+jinja

    {% extends 'manager/app_base.jinja' %}

    {% block javascript %}
    <script src="{{ static('custom/script.js') }}"></script>
    {% endblock %}

    {% block content %}
    <p>커스텀 서비스 내용</p>
    {% endcontent %}

메인 페이지(:file:`main.jinja`) 역시 서비스 기본 레이아웃과 마찬가지로 :file:`base.jinja` 를 상속받습니다.
특별한 경우에 내부의 ``div#main-spot`` 등을 수정할 수 있을 것입니다.


.. _django-modeltranslation: http://django-modeltranslation.readthedocs.io/en/latest/
.. _`Jinja 2`: http://jinja.pocoo.org/docs/2.9/
.. _django-jinja: http://niwinz.github.io/django-jinja/latest/
.. _DJANGO4KAIST: https://github.com/talkwithraon/tree/py3/
