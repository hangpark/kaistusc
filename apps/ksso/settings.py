# KAIST Portal Login System
# http://ctreq.kaist.ac.kr/static/docs/guide.pdf

import os

PORTAL_ADMIN_ID = os.getenv('PORTAL_ADMIN_ID')
PORTAL_ADMIN_PW = os.getenv('PORTAL_ADMIN_PW')
PORTAL_PUBLIC_KEY = os.getenv('PORTAL_PUBLIC_KEY')
PORTAL_LOGIN_URL = 'https://ksso.kaist.ac.kr/iamps/requestLogin.do'
PORTAL_TARGET_URL = 'https://iam.kaist.ac.kr/iamps/services/singlauth'
AUTH_REDIRECT_URL = '/'
