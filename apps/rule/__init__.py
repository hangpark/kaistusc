from django.utils.dateformat import DateFormat
from django.utils.translation import get_language
from django_jinja import library


def get_rule_date_format(lang):
    if lang == 'en':
        return 'F j, Y'
    return 'Y.m.d.'


def get_empty_date(lang):
    if lang == 'en':
        return 'Not Resolved.'
    return '0000.00.00.'


@library.filter
def rule_date(date):
    lang = get_language()
    if not date:
        return get_empty_date(lang)
    return DateFormat(date).format(get_rule_date_format(lang))
