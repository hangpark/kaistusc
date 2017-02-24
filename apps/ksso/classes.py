from xml.etree import ElementTree

import requests
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from . import settings
from .models import PortalInfo


class PortalController():
    """
    KAIST 단일인증서비스 서버와의 통신을 구현한 클래스.

    사용자가 KAIST 단일인증서비스 서버로부터 발급받은 토큰을 통해 서버사이드에서
    KAIST 단일인증서비스 서버와 SOAP 통신을 진행할 수 있도록 관련 기능을 구현한
    클래스입니다. KAIST 단일인증서비스 서버에서 넘겨주는 사용자 정보를 이용하여
    기존 사용자의 경우 정보 업데이트를, 신규 사용자의 경우 :class:`User` 와
    :class:`PortalInfo` 모델 인스턴스 추가를 진행할 수 있습니다.

    생성자로 토큰을 전달하면 :class:`AuthController` 에서 KAIST 단일인증서비스
    서버와 통신을 진행합니다. 통신 결과를 토대로 :class:`UserController` 에서는
    사용자를 추출하고 해당 사용자 정보 추가 또는 업데이트를 진행합니다. 이렇게
    인증된 사용자 인스턴스는 :attr:`user` 에 저장됩니다.

    :meth:`retrieve_user` 를 이용하여 사용자를 얻을 수 있으며, 이를 이용해
    로그인 처리를 할 수 있습니다.
    """

    def __init__(self, token):
        #: 인증 컨트롤러.
        self.auth_ctrl = self.AuthController(token)

        #: 인증 컨트롤러에 세팅된 요청에 대한 KAIST 단일인증서비스 서버의 응답
        self.user_data = self.auth_ctrl.connect()

        #: 사용자 컨트롤러.
        self.user_ctrl = self.UserController(self.user_data)

        #: 인증된 사용자 인스턴스.
        self.user = self.user_ctrl.session()

    def retrieve_user(self):
        """
        인증된 사용자 인스턴스를 반환하는 메서드.
        """
        return self.user

    class UserController():
        """
        KAIST 단일인증서비스 서버에서 보낸 데이터를 이용하여 사용자 인증 처리를
        하는 내부 클래스.

        데이터가 생성자에 전달되면 내부 클래스 :class:`PortalParser` 에 넘겨
        파서를 생성합니다. 이후 파서를 통해 UID를 추출하여 해당되는 사용자가
        등록되어 있는지 :class:`User` 모델을 검색합니다. 원칙적으로 UID가
        :class:`User` 인스턴스의 :attr:`username`, :attr:`password` 가 되고
        자세한 사용자 정보는 :class:`PortalInfo` 에 따로 저장됩니다.

        사용자가 기존에 등록되어 있는 경우 정보를 업데이트하고, 등록되어있지
        않은 경우 새로운 :class:`User` 인스턴스와 :class:`PortalInfo` 인스턴스를
        생성하여 데이터베이스에 저장합니다. :class:`PortalInfo` 인스턴스는
        전역변수 :attr:`portal_info` 에 저장됩니다.
        """

        def __init__(self, user_data):
            #: KAIST 단일인증서비스 서버에서 보낸 사용자 데이터 파서.
            self.parser = self.PortalParser(user_data)

            #: 사용자 UID.
            self.kaist_uid = self.parser.attr('kaist_uid')

            if self.kaist_uid is None:
                self.portal_info = None
                return

            # KAIST 단일서비스 인증정보가 저장되어 있는 경우
            # XML 정보를 바탕으로 database를 갱신합니다.
            try:
                self.portal_info = PortalInfo.objects.get(
                    kaist_uid=self.kaist_uid)
                self.update_portal_info()

            # KAIST 단일서비스 인증정보가 저장되어 있지 않을 경우
            # PortalInfo instance를 생성합니다.
            except PortalInfo.DoesNotExist:
                self.insert_portal_info()
                self.update_portal_info()

        def insert_portal_info(self):
            """
            사용자를 새로 등록하는 메서드.

            :class:`User` 인스턴스를 사용자 UID를 이용하여 생성하고 이렇게
            만들어진 인스턴스와 UID로 :class:`PortalInstance` 를 생성합니다.
            UID를 제외한 다른 사용자 정보는 :meth:`update_portal_info` 에서
            추가됩니다.
            """
            user = User.objects.create_user(username=self.kaist_uid,
                                            password=self.kaist_uid)
            user.save()
            self.portal_info = PortalInfo.create(user=user,
                                                 kaist_uid=self.kaist_uid)

        def update_portal_info(self):
            """
            사용자 정보를 갱신하는 메서드.

            :attr:`fields` 에 명시된 모델 필드의 값들을 파서를 통해 추출하여
            저장합니다.
            """
            self.portal_info.kaist_uid = self.parser.attr('kaist_uid')

            fields = [
                'ku_kname', 'ku_acad_prog', 'ku_std_no', 'ku_born_date',
                'ku_psft_user_status_kor', 'ku_sex', 'ou', 'mail', 'mobile']
            for field in fields:
                setattr(self.portal_info, field, self.parser.attr(field))
            self.portal_info.save()

        def session(self):
            """
            사용자를 인증하는 메서드.

            사용자 인증이 성공했을 때 해당하는 :class:`User` 인스턴스를 반환하며
            사용자 인증이 실패했을 때에는 :const:`None` 을 반환합니다.
            """
            if self.portal_info is None:
                return None
            user = authenticate(username=self.portal_info.user.username,
                                password=self.portal_info.user.username)
            return user

        class PortalParser():
            """
            KAIST 단일인증서비스 서버에서 보낸 데이터를 파싱하는 내부 클래스.
            """

            def __init__(self, user_data):
                self.data = ElementTree.fromstring(user_data.text)
                self.data = self.data.getchildren()[0]
                self.data = self.data.getchildren()[0]
                self.data = self.data.getchildren()[0]

            def attr(self, item):
                """
                XML 정보에서 전달된 아이템 값을 파싱하여 반환하는 메서드.

                파싱에 실패한 경우 빈 문자열을 반환합니다.
                """
                return self.data.findtext(item) or ""

    class AuthController():
        """
        KAIST 단일인증서비스와의 통신기능을 제공하는 내부 클래스.

        전달된 토큰을 바탕으로 요청문과 헤더를 정해진 형식에 맞춰 생성합니다.
        이후 내부의 :meth:`connect` 메서드를 호출하여 통신을 수행합니다.
        """

        def __init__(self, token):
            self.token = token
            self.request_string = self.build_request_string()
            self.request_header = self.build_request_header()

        def build_request_string(self):
            """
            정해진 형식에 맞춰 KAIST 단일인증서비스 서버로 보낼 요청문을
            작성하고 반환하는 메서드.
            """
            request_string = (
                '<soapenv:Envelope xmlns:soapenv='
                '"http://schemas.xmlsoap.org/soap/envelope/"'
                ' xmlns:ser="http://server.com">'
                '<soapenv:Header/>'
                '<soapenv:Body>'
                '<ser:verification>'
                '<cookieValue>{token}</cookieValue>'
                '<publicKeyStr>{public_key}</publicKeyStr>'
                '<adminVO>'
                '<adminId>{admin_id}</adminId>'
                '<password>{admin_pw}</password>'
                '</adminVO>'
                '</ser:verification>'
                '</soapenv:Body>'
                '</soapenv:Envelope>'
            ).format(
                token=self.token,
                public_key=settings.PORTAL_PUBLIC_KEY,
                admin_id=settings.PORTAL_ADMIN_ID,
                admin_pw=settings.PORTAL_ADMIN_PW
            )
            return request_string

        def build_request_header(self):
            """
            정해진 형식에 맞춰 KAIST 단일인증서비스 서버로 보낼 요청 헤더를
            작성하고 반환하는 메서드.
            """
            request_header = {
                'Content-type': 'text/xml;charset=\"utf-8\"',
                'Accept': 'text/xml',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Content-length': str(len(self.request_string))
            }
            return request_header

        def connect(self):
            """
            준비된 요청을 KAIST 단일인증서비스 서버로 보내고 그에 대한 응답을
            받아 반환하는 메서드.
            """
            response = requests.post(
                settings.PORTAL_TARGET_URL,
                data=self.request_string,
                headers=self.request_header)
            return response
