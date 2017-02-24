"""
게시판 앱.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BoardConfig(AppConfig):
    """
    게시판 커스텀 앱 설정.
    """

    name = 'apps.board'
    verbose_name = _("게시판")
