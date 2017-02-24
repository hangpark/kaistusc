"""
KAIST 단일인증시스템 설정.

관리자의 포탈 계정정보는 환경변수로부터 받아오게끔 하여 보안을 유지합니다.
"""

import os

#: 관리자 포탈 계정 ID.
PORTAL_ADMIN_ID = os.getenv('PORTAL_ADMIN_ID')

#: 관리자 포탈 계정 비밀번호.
PORTAL_ADMIN_PW = os.getenv('PORTAL_ADMIN_PW')

#: KAIST 단일인증시스템 공개키.
PORTAL_PUBLIC_KEY = os.getenv('PORTAL_PUBLIC_KEY')

#: KAIST 단일인증시스템 로그인 URL.
PORTAL_LOGIN_URL = 'https://ksso.kaist.ac.kr/iamps/requestLogin.do'

#: KAIST 단일인증시스템 인증 URL.
PORTAL_TARGET_URL = 'https://iam.kaist.ac.kr/iamps/services/singlauth'

#: 인증 후 리다이렉션 URL이 설정되지 않았을 경우 이동할 기본 URL.
AUTH_REDIRECT_URL = '/'
