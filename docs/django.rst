Django
===============================================

Django 프로젝트는 최상위 폴더 안의 :file:`manage.py` 파일과 :file:`kaistusc/` 내부의 설정파일들, 그리고 :file:`apps/` 내부의 세 개의 앱과 :file:`middlewares/` 내부의 한 개의 미들웨어로 구성되어 있습니다.

본 프로젝트에서는 i18n을 위해 django-modeltranslation_ 을 이용하여 사용자 작성 컨텐츠가 유동적으로 번역될 수 있도록 하였습니다.
또한, 템플릿은 `Jinja 2`_ 엔진을 사용하였으며 이는 django-jinja_ 라이브러리를 통해 지원되고 있습니다.
다만, 내장 템플릿 엔진 역시 사용이 가능하며, :file:`*.jinja` 파일은 **django-jinja** 로, :file:`*.html` 파일은 내장 템플릿 엔진으로 처리됩니다.
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

위의 예시에서 *"카테고리명"* 은 :attr:`name` 의 :attr:`verbose_name` 으로, 어드민 페이지나 폼 등에서 나타나는 문자열입니다.
이를 국제화하는 방법은 아래와 같습니다.

.. code-block:: python3

    from django.db import models
    from django.utils.translation import ugettext_lazy as _

    class Category(models.Model):
        name = models.CharField(_("카테고리명"), max_length=32, unique=True)

이후 :file:`manage.py` 의 :program:`makemessages` 명령어를 통해 :file:`*.po` 파일을 생성하고 이에 대한 지역화를 수행한 후 :program:`compilemessages` 명령어로 번역을 완료합니다.
이 때, 최소한 **영어** 번역은 완료하는 것이 본 프로젝트의 요구사항입니다.

또한, 게시글 등 사용자 입력 데이터의 경우 **django-modeltranslation** 을 이용하여 영어로 번역할 수 있는 방법을 제공해야 합니다.
위에서 언급했듯이, 자세한 사항은 django-modeltranslation_ 문서를 참고하시길 바랍니다.
*(새로운 DB 테이블을 사용하는 서비스를 생성하실 때 확인하시는 것이 좋을 것입니다.)*


코멘트
~~~~~~

각 모듈과 클래스 마다 docstring을 작성하여 코드를 읽는 사람으로 하여금 그 역할을 분명히 알 수 있도록 해야 합니다.
또한, 모델 필드의 경우 :attr:`verbose_name` 을 필수적으로 명시하여야 하며, :attr:`help_text` 작성 역시 권장합니다.
모델 클래스의 경우 메타 클래스에 :attr:`verbose_name` 과 :attr:`verbose_name_plural` 을 적어야 합니다.


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

**Manager** 앱은 요약하자면 사이트 내 서비스를 정의하고 관리하는, 사이트 관리 앱입니다.
:file:`models.py` 에는 :class:`Category` 와 :class:`Service` 모델이 정의되어 있습니다.
각 필드에 대한 설명은 :attr:`verbose_name` 에 담겨 있습니다.


서비스 권한
~~~~~~~~~~~

**Manager** 앱이 필요한 가장 큰 이유는 **권한 관리** 때문입니다.
기본적으로 kaistusc 프로젝트는 각 서비스에 대한 권한을 아래 7가지 중 하나로 나타냅니다. (:mod:`apps.manager.constants` 에 위치)

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

권한은 :class:`GroupServicePermission` 모델에 의해 관리됩니다.
각 서비스와 django가 기본으로 제공하는 그룹 기능 사이에 특정한 권한을 부여할 수 있습니다.
사용자가 여러 그룹에 속해있고 각 그룹이 특정 서비스에 서로 다른 권한을 지닌다면, 그 사용자는 해당 서비스에 대하여 각 그룹의 권한들 중 최고로 높은 권한을 갖게 됩니다.

특히, 서비스 모델 내의 :attr:`max_permission_anon` 과 :attr:`max_permission_auth` 를 이용하여 각각 비로그인 사용자, 로그인 사용자의 최대 권한을 설정할 수 있습니다.
이 경우 특정 사용자의 권한은 위의 최고 높은 그룹 권한과 이 필드의 값들을 비교하여 산출됩니다.
또한, :attr:`is_closed` 가 :const:`True` 로 설정된 경우, 기존에 갖고 있던 권한에 상관 없이 관리자를 제외한 사용자는 *권한없음* 상태가 됩니다.

권한여부를 확인하는 로직은 :meth:`is_permitted` 메소드에 구현되어 있으며, 아래와 같이 커스텀 매니저(:class:`ServiceManager`)와 쿼리셋 (:class:`ServiceQueryset`)을 통해 특정 유저가 접근가능한 서비스를 뽑아낼 수 있습니다.

.. code-block:: python3

    from apps.manager.models import Service

    # In view
    services = Service.objects.filter(
        category__name="카테고리").accessible_for(request.user)


서비스 뷰
~~~~~~~~~

각 서비스는 기본적으로 :mod:`apps.manager.views.base` 의 :class:`ServiceView` 를 상속받아 구현합니다.
이는 몇 가지 믹스인과 :class:`TemplateView` 로 이루어져 있는 뷰입니다.
이 중 :class:`PermissionRequiredServiceMixin` 은 권한이 없는 사용자가 서비스에 접근할 때 403 에러를 발생시킵니다.
기본으로는 *접근권한* 이 있는지 여부를 따지지만, :attr:`required_permission` 을 설정하여 다른 권한이 있을 것을 요구할 수 있습니다.

따라서 :class:`ServiceView` 를 상속하여 커스텀 서비스(예를 들어 :class:`CustomServiceView`)를 만들고, 해당 서비스 내부의 여러 뷰는 :class:`CustomServiceView` 를 상속하고 :attr:`required_permission` 을 조정하는 식으로 쉽게 구현할 수 있습니다.
자세한 응용 예시는 :mod:`apps.board.views` 모듈 소스코드를 참고하세요.

:class:`NavigatorMixin` 은 카테고리와 하위 접근 가능 서비스들의 계층 목록을 얻어 사이트 네비게이터를 생성합니다.
사이트 기본 레이아웃에 존재하는 네비게이션바 등을 구현하는 데에 쓰입니다.
이 믹스인과 :class:`TemplateView` 를 합친 :class:`PageView` 는 권한이 필요하지 않는 정적 서비스나 정적 페이지 등을 구현하는 데 요긴하게 쓰입니다.
활용 예시는 :mod:`apps.manager.views.statics` 모듈 소스코드를 참고하세요.


커스텀 에러
~~~~~~~~~~~

기본적으로 django는 404, 500, 403, 400 에러에 대해 이벤트 핸들러를 제공합니다.
이를 활용하면 사이트에서 에러 페이지를 커스터마이징 할 수 있습니다.
본 사이트에서도 커스텀 에러 페이지를 제공하고 있습니다.
각 종류의 에러마다 에러 문구가 다릅니다.
이를 테면, 404 에러의 경우 제목은 *'페이지가 존재하지 않습니다.'*, 내용은 *'클릭하신 링크가 잘못되었거나 페이지가 제거되었습니다.'* 로 구성된 에러 페이지가 나타납니다.

커스텀 에러는 각각의 상황에 맞는 에러 내용을 에러 페이지에 띄울 수 있도록 해줍니다.
:class:`Custom404`, :class:`Custom500`, :class:`Custom403`, :class:`Custom400` 에러 클래스가 :mod:`apps.manager` 에 정의되어 있습니다.
이를 이용하여 아래 예시와 같이 사용하시면 인자로 넘겨준 내용이 에러 페이지에 뜨게 됩니다.

.. code-block:: python3

    from django.utils.translation import ugettext_lazy as _

    from apps.manager import Custom404

    raise Custom404(_("존재하지 않는 게시글입니다."))


템플릿
~~~~~~

**Manager** 앱은 사이트 기본 레이아웃을 정의한 템플릿을 제공합니다.
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


apps.ksso (KAIST 단일인증서비스)
--------------------------------

- :file:`apps/ksso/`

총학생회 사이트의 인증체계는 기본적으로 **KAIST 단일인증서비스** 를 이용합니다.
포탈 계정을 통해 로그인이 가능하게 하는 것입니다.
물론 단체 계정, 루트 계정 등은 django의 기본 :class:`User` 모델을 이용하며, ``/admin`` 에서 로그인합니다.


DJANGO4KAIST
~~~~~~~~~~~~

DJANGO4KAIST_ 는 **KAIST 단일인증서비스 v3.0** 을 django로 구현하는 프로젝트입니다.
김강인_ 제29대 총학생회장이 완성하였으며, 박항_ 제30대 부총학생회장이 파이썬 3 버전으로 수정하였습니다.
**ksso** 이름의 django 앱으로 만들어져 있습니다.
본 프로젝트에서는 이 **ksso** 앱을 수정하여 사용하고 있습니다.
이 문서에는 기본사항만 담겨있습니다.
자세한 내용은 DJANGO4KAIST_ :file:`README` 문서를 참고하시길 바랍니다.

참고로 **KAIST 단일인증서비스 v3.0** 은 등록된 아이피에서 443 포트로 HTTPS 통신을 해야만 사용하실 수 있습니다.
따라서 로컬에서 테스트하기가 어려운 면이 있습니다.


포탈 계정 정보
~~~~~~~~~~~~~~

**KAIST 단일인증서비스** 를 이용하여 로그인을 알맞게 하게 되면 KAIST 학교당국으로부터 총학생회 서버로 사용자의 개인정보가 전달됩니다.
기본 인증모델은 django 내장 :class:`User` 모델을 사용하며, ID와 패스워드 둘 다 전달받은 사용자의 UID로 설정합니다.
(이 경우 패스워드가 암호화되기 때문에 나중에 UID를 패스워드로 입력하여도 해시값이 일치하지 않아 직접 로그인이 불가능합니다.)
:class:`User` 모델을 확장하기 위해서 **ksso** 앱에서는 :class:`PortalInfo` 라는 모델을 정의하고 이를 :class:`User` 모델과 1-1 대응을 시킵니다.
이 :class:`PortalInfo` 의 각 필드에는 전달된 사용자의 개인정보가 저장됩니다.

본 프로젝트가 KAIST로부터 허가 받은 사용자의 개인정보는 아래와 같습니다.

- 이름 (:attr:`ku_kname`)
- 고유번호(UID) (:attr:`kaist_uid`)
- 학위과정 (:attr:`ku_acad_prog`)
- 학번 (:attr:`ku_std_no`)
- 학적상태 (:attr:`ku_psft_user_status_kor`)
- 생년월일 (:attr:`ku_born_date`)
- 성별 (:attr:`ku_sex`)
- 학과 (:attr:`ou`)
- 메일주소 (:attr:`mail`)
- 전화번호 (:attr:`mobile`)


개인정보는 합법적 테두리 안에서 최소한으로 활용해야 하며, 유지보안에 심혈을 기울여야 합니다.


로그인/로그아웃
~~~~~~~~~~~~~~~

``/user/login/`` 와 ``/user/logout/`` 에 접속하면 각각 :class:`LoginView`, :class:`LogoutView` 를 통해 로그인 절차가 진행됩니다.
데이터베이스에 저장되어 있는 :class:`PortalInfo` 는 기존 사용자가 재로그인을 할 때 해당 시점에 맞게 업데이트 됩니다.
따라서 :class:`PortalInfo` 에 저장된 정보는 최신 정보가 아닐 수 있습니다.

로그인과 로그아웃 URL 뒤 ``next`` 파라미터를 통해 로그인/아웃 처리 후 이동할 경로를 지정할 수 있습니다.
로그인의 경우 *단일 서비스 인증 페이지* 에서 인증을 담당하기 때문에 리다이렉션 경로 저장을 위해 쿠키를 사용합니다.
아래는 로그인 후 *about* 페이지로 이동하는 예시입니다.

.. code-block:: html

    <a href="/user/login/?next=/about/">로그인 후 about 페이지 이동</a>


정보제공 동의절차
~~~~~~~~~~~~~~~~~

기존 **DJANGO4KAIST** 에서 제공하는 기능에 더하여 본 프로젝트에서는 **정보제공 동의절차** 를 구현하였습니다.
사용자가 본인의 개인정보 제공에 동의할 때에만 사이트를 이용할 수 있도록 최초 로그인 시 정보제공 동의페이지로 이동시킵니다.
여기서 동의하지 않을 경우 :class:`User` 모델과 :class:`PortalInfo` 모델 인스턴스를 삭제하고 로그아웃 처리합니다.
일련의 과정은 :mod:`apps.ksso.views` 모듈의 :class:`SignUpView`, :class:`AgreeView`, :class:`DisagreeView` 에 구현되어 있습니다.

정보제공 동의절차 기능에 있어 중요한 점은 사용자가 동의페이지에서 아무런 선택을 하지 않은 채 사이트를 이탈할 가능성이 있다는 점입니다.
이에 대한 해결책으로 :class:`PortalInfo` 모델에 :attr:`is_signed_up` 필드를 추가하여 정보제공 동의여부를 기록할 수 있도록 하였습니다.
또한, 아직 동의여부를 선택하지 않은 사용자의 개인정보가 DB 상에 존재하는 문제점을 최대한 해결하기 위하여 시스템 관리자를 제외하고 사이트 관리자, 스태프 등이 정보를 활용하지 못하도록 :attr:`is_signed_up` 이 :const:`True` 인 사용자만 필터링한 :class:`PortalInfoManager` 를 기본 매니저로 설정하였습니다.
따라서 사이트 관리자, 스태프 등 어드민 페이지 이용 권한이 있는 자들은 동의여부 선택하지 않은 사용자의 개인정보를 확인할 수 없게 됩니다.

직접적으로 모든 사용자를 다뤄야 할 경우가 있다면 :class:`PortalInfo` 의 :attr:`all_objects` 매니저를 이용하시면 됩니다.
:class:`ServiceView` 를 상속받아 구현된 모든 서비스들은 :class:`SignUpRequiredMixin` 이 최우선적으로 발동하여 :attr:`is_signed_up` 이 :const:`False` 일 경우에 자동적으로 정보제공 동의페이지로 이동하게 됩니다.


apps.board (게시판)
-------------------

- :file:`apps/board/`

**Board** 앱은 사이트의 기본 게시판 기능을 구현합니다.
게시판, 게시글, 댓글, 첨부파일, 태그 등 다양한 기능을 제공합니다.
:mod:`apps.board.models` 모듈 내에 위치한 :class:`Board` 모델은 :class:`Service` 모델을 상속받습니다.
따라서 여타 서비스와 같이 일괄적인 관리가 가능합니다.
기본적으로 게시판은 게시글의 집합으로, 게시글 기능 어떻게 구현하느냐가 더 중요하다고 말할 수 있습니다.


포스트 권한
~~~~~~~~~~~

게시글과 댓글은 모두 :class:`BasePost` 를 상속받습니다.
이 :class:`BasePost` 모델에는 권한 관리를 위하여 :meth:`is_permitted` 메서드가 정의되어 있습니다.
:meth:`is_permitted` 는 게시글, 댓글 등 여러 포스트 상속 모델들의 권한 설정을 커스터마이징 할 수 있도록 :meth:`pre_permitted` 와 :meth:`post_permitted` 메서드를 호출합니다.
이들은 기본적으로 :const:`True` 를 리턴하고 있으며, 게시글 댓글 등 포스트 상속 모델에서 두 메서드를 필요 시 오버라이드 하는 방식으로 활용할 수 있습니다.

예를 들어, 댓글을 구현한 :class:`Comment` 모델의 경우 :meth:`pre_permitted` 에서 댓글이 달린 포스트의 *읽기권한* 을 요구합니다.
그리고 :meth:`post_permitted` 에서는 댓글이 달린 포스트가 속한 게시판에서 사용자가 요청한 권한을 갖고있는지 여부를 판단합니다.

.. code-block:: python3

    # apps/board/models.py

    class Comment(BasePost):

        ...

        def pre_permitted(self, user, permission):
            return self.parent_post.is_permitted(user, PERM_READ)

        def post_permitted(self, user, permission):
            return self.parent_post.board.is_permitted(user, permission)

이런 식으로 기본적인 포스트 권한 체크 전후로 해당 포스트(위의 예제에서는 댓글)와 연결된 상위 모델들의 권한을 체크하여 연동하는 등 추가적인 로직을 손쉽게 구현할 수 있습니다.


사용자 활동 기록
~~~~~~~~~~~~~~~~

각 포스트에 조회, 추천, 비추천과 같은 사용자 반응이나 특정 활동을 기록할 수 있는 기능을 제공합니다.
기본 사용자 활동으로 조회, 추천/비추천 두 가지가 구현되어 있습니다.
이 외의 활동 역시 손쉽게 추가하여 제공하는 기능을 확장하실 수 있습니다.

.. code-block:: python3

    # apps/board/models.py

    # Post Activities
    ACTIVITY_VIEW = 'VIEW'
    ACTIVITY_VOTE = 'VOTE'

:class:`PostActivity` 모델은 사용자, IP 주소, 포스트, 활동구분 4가지 정보를 저장합니다.
기본적으로 동일 포스트에는 특정 활동을 사용자 당 한 번만 하도록 허용하고 있습니다.
사용자가 로그인을 하지 않았을 경우 IP 주소로 이를 갈음합니다.
이 :class:`PostActivity` 모델은 :class:`BasePost` 모델과 :class:`User` 모델 사이의 다대다 관계에서 중간모델_ 역할을 합니다.

:class:`BasePost` 모델의 :meth:`get_acitivity_count` 메서드를 통해 특정 활동이 몇 번 이루어졌는지 집계할 수 있습니다.
또한, :meth:`assign_activity` 는 특정 유저의 활동을 추가합니다.
이 두 메서드를 통해 조회와 추천/비추천 두 활동 외에도 다양한 활동을 구현할 수 있습니다.
:meth:`assign_activity` 매서드는 이미 활동을 한 사용자의 경우 아무런 처리를 하지 않고 :const:`False` 를 리턴합니다.
처음 활동을 하는 경우 활동을 등록하고 :const:`True` 를 리턴합니다.
이 리턴값을 가지고 활동 처리 후 추가 로직을 뷰 차원에서 구현할 수도 있을 것입니다.

위 두 메서드를 조회 활동에 한정시킨 메서드 :meth:`get_hits`, :meth:`assign_hits` 가 존재하며, shortcut 개념으로 이해하면 됩니다.

추천/비추천의 경우 동일한 활동으로 기록되며, 이는 특정 사용자가 추천을 했는지 비추천을 했는지 파악하지 못하도록 하기 위함입니다.
따라서 위에서 언급한 뷰 차원의 추가 로직을 통해 :class:`BasePost` 모델에 마련되어 있는 :attr:`vote_up` 과 :attr:`vote_down` 필드를 단발적으로 증가시키는 형태로 추천/비추천 수를 기록합니다.

.. code-block:: python3

    # apps/board/views.py::PostVoteView::post

    ...

    is_new = post.assign_activity(request, ACTIVITY_VOTE)
    if is_new:
        if kwargs['mode'] == 'up':
            post.vote_up += 1
        if kwargs['mode'] == 'down':
            post.vote_down += 1
        post.save()
    return HttpResponse(is_new)


포스트 뷰
~~~~~~~~~

게시글을 보여주는 :class:`PostView` 는 :class:`BoardView` 를 상속받습니다.
그런데 단순히 게시판 권한 체크 로직만 따라가면 개별 포스트에 대한 권한 체크가 이뤄지지 않습니다.
이를 해결하기 위해 :class:`PostView` 는 :class:`PermissionRequiredServiceMixin` 의 :meth:`has_permission` 을 오버라이드 하여 개별 포스트 권한 체크를 시행하고 있습니다.
:meth:`has_permission` 에서 사용되는 :attr:`required_permission` 값을 기본 *읽기권한* 으로 설정하였습니다.
그리고 우선적으로 :meth:`super` 메서드를 통해 게시판 *접근권한* 이 있는지 체크한 후 :class:`Post` 객체를 추출하여 저장합니다.
마지막으로 이 객체에 대한 이용권한을 테스트하고 그 여부를 리턴하고 있습니다.

위 과정은 :class:`PermissionRequiredServiceMixin` 을 어떻게 활용하고 확장할 것인가에 대한 좋은 예시라고 생각합니다.
더욱 주목해야 할 점은, 이러한 :class:`PostView` 를 상속하여 게시글을 수정하는 :class:`PostEditView`, 게시글을 삭제하는 :class:`PostDeleteView`, 댓글을 작성하는 :class:`CommentWriteView`, 댓글을 삭제하는 :class:`CommentDeleteView`, 게시글 추천기능을 관장하는 :class:`PostVoteView` 등이 구현되었다는 점입니다.
예를 들어, :class:`PostDeleteView` 의 경우 :attr:`required_permission` 을 *삭제권한* 으로만 설정하고 삭제로직만 추가하면 구현이 완료되는 것입니다.

.. code-block:: python3

    # apps/board/views.py

    class PostDeleteView(PostView):

    template_name = None
    required_permission = PERM_DELETE

    def post(self, request, *args, **kwargs):
        post = self.post_
        post.is_deleted = True
        post.save()
        return HttpResponseRedirect(post.board.get_absolute_url())


위와 같이 상속기능을 이용하여 손쉽게 많은 기능들을 구현할 수 있습니다.


middlewares.locale (다국어 지원)
--------------------------------

- :file:`middlewares/locale.py`

**Locale** 모듈은 세션을 통해 사용자가 원하는 언어로 사이트를 이용할 수 있게끔 지원하는 기능을 제공합니다.
기본적으로 사용자 로케일이 전달되어 이를 변경하여 다른 언어로 사이트를 이용하기에는 번잡스러운 부분이 많습니다.
그러나 본 모듈 내 있는 :class:`SessionBasedLocaleMiddleware` 는 사용자가 한 번 URL 상 GET 파라미터 ``lang`` 을 통해 언어코드를 전달하면 로케일을 변경하고 이를 세션에 저장하여 지속성을 유지합니다.

본 미들웨어는 schmidsi_ 님의 `Set language via HTTP GET Parameter`_ 코드를 django 1.10 버전에 맞게 수정한 것입니다.


.. _django-modeltranslation: http://django-modeltranslation.readthedocs.io/en/latest/
.. _`Jinja 2`: http://jinja.pocoo.org/docs/2.9/
.. _django-jinja: http://niwinz.github.io/django-jinja/latest/
.. _DJANGO4KAIST: https://github.com/talkwithraon/tree/py3/
.. _김강인: https://github.com/talkwithraon/
.. _박항: https://github.com/hangpark/
.. _중간모델: https://docs.djangoproject.com/en/1.10/topics/db/models/#intermediary-manytomany/
.. _schmidsi: https://github.com/schmidsi/
.. _`Set language via HTTP GET Parameter`: https://djangosnippets.org/snippets/1948/
