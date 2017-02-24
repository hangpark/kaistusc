"""
KAIST 단일인증서비스.

KAIST에서 제공하는 단일인증서비스 v3.0(KAIST Single Auth Service v3.0)을
이용하여 인증 처리를 진행하는 앱입니다. DJANGO4KAIST 프로젝트의 ksso 앱을
수정하여 정보제공 동의절차 등의 기능을 추가된 버전입니다.
"""

default_app_config = 'apps.ksso.apps.KssoConfig'
