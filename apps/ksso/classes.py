# -*- coding:utf-8 -*-

from . import settings
from .models import PortalInfo


class PortalController():

    def __init__(self, token):
        self.auth_ctrl = self.AuthController(token)
        self.user_data = self.auth_ctrl.connect()
        self.user_ctrl = self.UserController(self.user_data)
        self.user = self.user_ctrl.session()

    def retrieve_user(self):
        return self.user

    class UserController():

        def __init__(self, user_data):
            self.parser = self.PortalParser(user_data)
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

        # PortalInfo instance를 생성합니다.
        def insert_portal_info(self):
            from django.contrib.auth.models import User
            user = User.objects.create_user(username=self.kaist_uid,
                                            password=self.kaist_uid)
            user.save()
            self.portal_info = PortalInfo.create(user=user,
                                                 kaist_uid=self.kaist_uid)

        # PortalInfo를 갱신합니다.
        def update_portal_info(self):
            self.portal_info.kaist_uid = self.parser.attr('kaist_uid')
            self.portal_info.ku_kname = self.parser.attr('ku_kname')
            self.portal_info.ku_acad_prog = self.parser.attr('ku_acad_prog')
            self.portal_info.ku_std_no = self.parser.attr('ku_std_no')
            self.portal_info.ku_psft_user_status_kor = self.parser.attr('ku_psft_user_status_kor')
            self.portal_info.ku_born_date = self.parser.attr('ku_born_date')
            self.portal_info.ku_sex = self.parser.attr('ku_sex')
            self.portal_info.ou = self.parser.attr('ou')
            self.portal_info.mail = self.parser.attr('mail')
            self.portal_info.mobile = self.parser.attr('mobile')
            
            self.portal_info.save()

        def session(self):
            if self.portal_info is None:
                return None
            from django.contrib.auth import authenticate
            user = authenticate(username=self.portal_info.user.username,
                                password=self.portal_info.user.username)
            return user

        class PortalParser():

            def __init__(self, user_data):
                from xml.etree import ElementTree
                self.data = ElementTree.fromstring(user_data.text)
                self.data = self.data.getchildren()[0]
                self.data = self.data.getchildren()[0]
                self.data = self.data.getchildren()[0]

            # XML 정보를 파싱하여서 리턴합니다.
            def attr(self, item):
                return self.data.findtext(item)

    class AuthController():

        def __init__(self, token):
            self.token = token
            self.request_string = self.build_request_string()
            self.request_header = self.build_request_header()

        # request string 을 만듭니다.
        def build_request_string(self):
            request_string = '<soapenv:Envelope xmlns:soapenv='
            request_string += '"http://schemas.xmlsoap.org/soap/envelope/"'
            request_string += ' xmlns:ser="http://server.com">'
            request_string += '<soapenv:Header/>'
            request_string += '<soapenv:Body>'
            request_string += '<ser:verification>'
            request_string += '<cookieValue>' + self.token
            request_string += '</cookieValue>'
            request_string += '<publicKeyStr>' + settings.PORTAL_PUBLIC_KEY
            request_string += '</publicKeyStr>'
            request_string += '<adminVO>'
            request_string += '<adminId>' + settings.PORTAL_ADMIN_ID
            request_string += '</adminId>'
            request_string += '<password>' + settings.PORTAL_ADMIN_PW
            request_string += '</password>'
            request_string += '</adminVO>'
            request_string += '</ser:verification>'
            request_string += '</soapenv:Body>'
            request_string += '</soapenv:Envelope>'
            return request_string

        # request header 를 만듭니다.
        def build_request_header(self):
            request_header = {
                    'Content-type': 'text/xml;charset=\"utf-8\"',
                    'Accept': 'text/xml',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'Content-length': str(len(self.request_string))
            }
            return request_header

        # requests를 이용하여 연결합니다.
        def connect(self):
            import requests
            response = requests.post(
                    settings.PORTAL_TARGET_URL,
                    data=self.request_string,
                    headers=self.request_header)
            return response
