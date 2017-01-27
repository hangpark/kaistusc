from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BoardConfig(AppConfig):
    name = 'apps.board'
    verbose_name = _("게시판")
