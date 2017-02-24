"""
사이트 관리 도구 앱.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ManagerConfig(AppConfig):
    """
    사이트 관리 도구 커스텀 앱 설정.
    """

    name = 'apps.manager'
    verbose_name = _("사이트 관리도구")
