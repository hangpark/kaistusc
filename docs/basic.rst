프로젝트 기본사항
===============================================


들어가기
-----------------------------------------------

KAIST USC 프로젝트는 KAIST 학부 총학생회 사이트를 구축하여 총학생회 회원들의 원활한 참여를 보장하기 위해 시작되었습니다.
2016년 제30대 KAIST 학부 총학생회 <K'loud> 중앙집행국에서 프로젝트를 운영하였으며, 제31대 KAIST 학부 총학생회 <품>에게 인수인계를 하여 지속적으로 개발 중에 있는 상황입니다.

KAIST USC 프로젝트는 단순한 공지 및 보드 형식의 일반적인 사이트와는 달리 몇 가지 차별화된 개발 원칙과 방향성을 갖고 있습니다.

(1) **다양한 서비스 개발을 위한 통합 플랫폼**

총학생회의 여러 사업과 연계하여 단기간에 각 사업에 맞는 서비스를 개발하고 이를 사이트에 배포할 수 있도록 사이트 차원에서 손쉽게 개발을 할 수 있는 인프라를 조성합니다. 
각각의 서비스는 Django_ 의 *어플리케이션(app)* 형식으로 개발되어 사이트에 탈부착 하기가 용이합니다.
서비스의 권한과 특성 관리를 위해 사이트 내의 서비스들을 통합하여 관리할 수 있는 시스템을 갖추었습니다.

또한, 서비스 개발 시 KAIST Portal 계정으로 통합된 유저모델이나 이미 구현된 사이트 내부 구성요소 view 등 여러 기능들을 자유롭게 활용하여 보다 빠르게 개발할 수 있고, 특히 유저 개개인의 권한이나 공통된 집단의 구성원을 묶은 그룹 등 Django에서 제공하는 강력한 기능들을 사용하실 수 있습니다.

(2) **다양한 구성원을 포용하는 다국어 지원**

KAIST의 많은 국제학생들 역시 총학생회 활동에 소외되지 않도록 철저한 다국어 지원을 원칙으로 개발되었습니다.
고정된 페이지 컨텐츠의 경우 :program:`gettext` 를, 사용자 입력 데이터의 경우 :program:`django-modeltranslation` 을 이용하여 원활한 다국어 지원을 하고 있습니다.

(3) **다양한 실행환경을 대비한 반응형 웹디자인**

노트북, 핸드폰 등 다양한 기기 지원을 위해 반응형 웹디자인을 적용하여 사용자 편의를 높였습니다.
한 번의 개발로 다양한 실행환경을 포괄할 수 있게 하여 신속한 서비스 구현을 가능케 합니다.

(4) **지속성 있는 유지보수를 위한 문서화**

총학생회의 특성 상 세대교체가 빠르게 일어난다는 점에서 체계적인 인수인계는 필수적입니다.
역사적으로 보았을 때에도 수많은 홈페이지가 개발되었고, 그 중 상당수는 실질적인 서비스 시작을 하지도 못하고 사장되었습니다.
이번 사이트가 지속적 있는 총학생회 사이트로 남도록 하여 개발에 드는 불필요한 인력 및 자원 낭비를 매년의 총학생회가 하지 않도록 체계적인 문서화를 개발과 동시에 진행하고 있습니다.


프로젝트 기술 스택
-----------------------------------------------

**배포환경**

- Docker_
- Ubuntu_ 16.04
- MySQL_ 5.7
- Nginx_

**백엔드**

- Python_ 3.6
- uWSGI_ 2.0
- Django_ 1.10

**프론트엔드**

- Jinja_ 2.9
- jQuery_ 3.1
- `Bootstrap for Sass`_ 3.3
- `Font Awesome`_ 4.7

**기타**

- npm_, Gulp_, Bower_, Sphinx_


프로젝트 구조
-----------------------------------------------

본 프로젝트 파일구조는 크게 배포환경 설정파일, 백엔드 소스, 프론트엔드 소스, 개발문서로 나뉩니다.
최상위 폴더(:file:`kaistusc/`)에 있는 낱개의 파일들은 보통 배포환경을 구축하기 위한 설정파일들이며, 백엔드 소스는 :file:`kaistusc/`, :file:`apps/`, :file:`middlewares/` 에 담겨있으며, 프론트엔드 소스는 :file:`static/src/` 에, 개발문서는 :file:`docs/` 에 위치해 있습니다.

아래는 프로젝트 최상위 폴더에 존재하는 디렉토리와 파일들에 대한 간략한 설명입니다.
알파벳 순으로 나열되어 있습니다.

- **apps/**

Django 프로젝트 커스텀 앱을 모아놓는 디렉토리입니다.
:program:`django-admin startapp` 명령어를 통해 앱을 생성하면 기본적으로 프로젝트 최상위 폴더에 앱 디렉토리가 생기지만, 보다 원활한 관리를 위해 사용자가 제작한 커스텀 앱은 모두 :file:`apps` 내부에 보관하는 것을 원칙으로 합니다.

기본적으로 게시판 기능을 구현한 :program:`board` 앱, `KAIST 단일인증서비스`_ 를 이용하여 포탈 계정 로그인을 구현한 :program:`ksso` 앱, 사이트 구조와 내부 서비스를 관리하고 접근권한을 설정하는 :program:`manager` 앱 세 개가 포함되어 있습니다.

- **docs/**

Sphinx로 생성한 사이트 개발문서가 들어있습니다.
:file:`*.rst` 파일들이 reStructuredText_ 로 작성된 문서 원본이며, :program:`make html` 명령어를 실행하게 되면 :file:`docs/_build/html/` 내부에 HTML 파일들이 생성됩니다.
:program:`Nginx` 에서는 :file:`docs/_build/html/` 를 참조하여 개발문서 페이지를 제공합니다.

- **kaistusc/**

Django 프로젝트 설정파일이 담겨있는 프로젝트 관리 디렉토리입니다. :file:`settings.py` 나 :file:`urls.py`, :file:`wsgi.py` 등 :program:`django-admin startproject` 를 실행하면 생성되는 기본 프로젝트 파일들이 있습니다.

- **locale/**

외국어 번역 파일(:file:`*.po`, :file:`*.mo`)이 담겨 있습니다. 기본적으로 영어 번역이 존재하며, :file:`*.py`, :file:`*.html`, :file:`*.jinja` 파일이 기본 번역 대상입니다.

- **middlewares/**

Django 프로젝트에서 사용되는 커스텀 미들웨어가 들어있습니다. 기본으로 있는 :file:`locale.py` 는 사용자가 설정한 언어로 페이지를 보여주는 기능을 지원합니다.

- **static/**

프론트엔드 스태틱 파일과 소스가 담겨있습니다. :file:`static/src/` 에 프론트엔드 소스파일이 있으며, 이를 :program:`gulp` 를 통해 배포 버전으로 빌드하게 되면 그 결과가 :file:`static/dist/` 에 저장됩니다.
물론 django의 :program:`collectstatic` 명령은 :file:`static/` 전체 파일이 아닌, :file:`static/dist/` 내부 파일만 수집합니다.
:file:`static/src/javascript/` 에는 자바스크립트 소스가, :file:`static/src/stylesheets/` 에는 Sass 소스가 담겨져 있습니다.
  
- **.dockerignore**

Docker ignore 파일입니다.

- **.gitignore**

Git ignore 파일입니다.
디펜던시들은 모두 무시되기 때문에 :file:`requirements.txt`, :file:`package.json`, :file:`bower.json` 등을 통해 다운로드 및 설치를 진행해야 합니다.

- **Dockerfile**

웹서버 이미지 빌드를 위한 도커 파일입니다. 기본적으로 우분투 16.04 환경에서 돌아가며, 아래 순서대로 빌드됩니다.

    (1) 패키지 설치
    (2) :file:`nginx.conf` 를 이용한 웹서버 설정
    (3) :file:`package.json` 을 이용한 프론트엔드 빌드 도구 설치 및 :file:`bower.json` 을 이용한 프론트엔드 라이브러리 다운로드
    (4) 파이썬 가상환경 설정 및 :file:`requirements.txt` 를 이용한 파이썬 라이브러리 설치
    (5) 프로젝트 복사
    (6) :file:`gulpfile.js` 를 이용한 프론트엔드 소스 빌드 및 스태틱 수집
    (7) 개발문서 생성
    (8) Django 배포모드, 서버 인코딩, 포트 등 설정

- **README.md**

프로젝트 설명 문서입니다.

- **bower.json**

프론트엔드 디펜던시가 명시된 문서입니다. :program:`bower` 를 통해 설치합니다.

- **docker-entrypoint.sh**

도커 컨테이너가 실행될 때 수행되는 작업입니다. Django 마이그레이션을 진행하고 :program:`uWSGI`, :program:`Nginx` 를 실행합니다.

- **gulpfile.js**

프론트엔드 소스파일을 배포환경에 맞게 빌드하는 :program:`gulp` 파일입니다.

- **manage.py**

Django 프로젝트 매니지 파일입니다.

- **mysql.cnf**

:program:`MySQL` 기본 설정파일입니다. 문자셋이나 바인드 주소에 관한 설정이 추가되어 있습니다.

- **nginx.conf**

:program:`Nginx` 설정파일입니다. 스태틱 파일, 미디어 파일, 개발문서를 제외한 나머지 요청은 UNIX 소켓으로 연결합니다. HTTPS 설정이 적용되어 있습니다.

- **package.json**

프론트엔드 빌드 도구들이 명시된 파일입니다. :program:`npm` 을 이용하여 설치합니다. 

- **requirements.txt**

파이썬 디펜던시가 명시된 파일입니다. :program:`pip` 을 이용하여 일괄 설치할 수 있습니다.

- **uwsgi.ini**

:program:`uWSGI` 를 이용한 웹어플리케이션 서버 설정 파일입니다.


기여자 목록
-----------------------------------------------

- **박항** <hangpark@kaist.ac.kr> - 프로그래밍, 문서화
- **박병훈** - 웹디자인
- **권용석** - 웹디자인

.. _Docker: https://www.docker.com/
.. _Ubuntu:
.. _MySQL: https://www.mysql.com/
.. _Nginx: https://www.nginx.com/resources/wiki/
.. _Python:
.. _uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/
.. _Django: https://djangoproject.com/
.. _Jinja: http://jinja.pocoo.org/docs/2.9/
.. _jQuery: https://jquery.com/
.. _`Bootstrap for Sass`: https://github.com/twbs/bootstrap-sass/
.. _`Font Awesome`: http://fontawesome.io/
.. _npm: https://npmjs.com/
.. _Gulp: http://gulpjs.com/
.. _Bower: https://bower.io/
.. _Sphinx: http://www.sphinx-doc.org/en/stable/
.. _`KAIST 단일인증서비스`: https://github.com/talkwithraon/DJANGO4KAIST/tree/py3/
