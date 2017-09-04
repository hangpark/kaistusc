from django.utils.translation import ugettext as _


def get_choices(type_set):
    return list(type_set.values())


def get_verbose(type_set, name):
    value_dict = dict(list(type_set.values()))
    return value_dict[name]

# 규정 종류
RULE_TYPE = {
    'CONSTITUTION': ('CONST', _('회칙')),
    'BYLAW': ('BYLAW', _('세칙')),
    'RULE': ('RULE', _('규칙')),
    'ETC': ('ETC', _('기타규정')),
}

# 챕터 종류
CHAPTER_TYPE = {
    'PREAMBLE': ('PRE', _('전문')),
    'CHAPTER': ('CHAP', _('장')),
    'SECTION': ('SEC', _('절')),
    'SUPPLEMENT': ('SUPPL', _('부칙')),
}

# 제개정 종류
REVISION_TYPE = {
    'ESTABLISH': ('ESTAB', _('제정')),
    'PARTIALLY': ('PART', _('일부개정')),
    'FULLY': ('FULL', _('전부개정')),
}
