from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class KssoConfig(AppConfig):
    name = 'apps.ksso'
    verbose_name = _("KAIST 단일인증서비스")
