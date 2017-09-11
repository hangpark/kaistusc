from django.db import models
from django.utils.translation import ugettext as _

from apps.rule.const import get_choices, get_verbose, RULE_TYPE, CHAPTER_TYPE, REVISION_TYPE

from itertools import chain


class RuleSet(models.Model):
    """
    개정연혁에 따라 존재하는 같은 종류의 규정들을
    한데 묶은 규정세트.
    """

    slug = models.CharField(
        _('축약 영문구'),
        max_length=16)

    is_main = models.BooleanField(
        _('기본 규정여부'),
        default=False)

    class Meta:
        verbose_name = _('규정세트')
        verbose_name_plural = _('규정세트(들)')

    def __str__(self):
        first = self.rules.first()
        if first:
            return first.name
        return _('(비어있음)')

    def get_absolute_url(self):
        return '/usc/rule/{}'.format(self.slug)


class Rule(models.Model):
    """
    규정.
    """

    rule_set = models.ForeignKey(
        RuleSet,
        related_name='rules',
        verbose_name=_('규정세트'))

    name = models.CharField(
        _('규정명'),
        max_length=64)

    rule_type = models.CharField(
        _('종류'),
        max_length=8, choices=get_choices(RULE_TYPE))

    @property
    def rule_type_v(self):
        return get_verbose(RULE_TYPE, self.rule_type)

    @rule_type_v.setter
    def rule_type_verbose(self, value):
        self.rule_type = value

    revision_type = models.CharField(
        _('제개정 종류'),
        max_length=8, choices=get_choices(REVISION_TYPE))

    @property
    def revision_type_v(self):
        return get_verbose(REVISION_TYPE, self.revision_type)

    @revision_type_v.setter
    def revision_type_verbose(self, value):
        self.revision_type = value

    date_resolved = models.DateField(
        _('의결일'),
        null=True, blank=True)

    class Meta:
        ordering = ['-date_resolved']
        verbose_name = '규정'
        verbose_name_plural = '규정(들)'

    def __str__(self):
        return "{} ({} {})".format(
            self.name,
            self.date_resolved,
            get_verbose(REVISION_TYPE, self.revision_type))

    @property
    def d_chapters(self):
        q = self.chapters.filter(parent_chapter=None)
        ordering = ['PREAMBLE', 'CHAPTER', 'SECTION', 'SUPPLEMENT']
        chapter_type_list = [CHAPTER_TYPE[chapter_type][0] for chapter_type in ordering]
        q_list = [q.filter(chapter_type=chapter_type) for chapter_type in chapter_type_list]
        return list(chain(*q_list))

    @property
    def d_articles(self):
        return self.articles.filter(
            chapter=None)

    @property
    def d_clauses(self):
        return self.clauses.filter(
            chapter=None, article=None)

    @property
    def prev_rule(self):
        if self.date_resolved:
            return Rule.objects.filter(date_resolved__lt=self.date_resolved).order_by(
                '-date_resolved').first()
        return Rule.objects.order_by('-date_resolved').first()

    def get_revision_url(self):
        return '/revision/title'

    @property
    def revision_class(self):
        if self.prev_rule:
            return 'revised'
        return 'new'

    def get_parents(self):
        return []

    @property
    def verbose(self):
        return self.name


class Chapter(models.Model):
    """
    챕터.

    전문, 부칙이 아님에도 불구하고 번호가 없는 챕터는
    최하위 순서로 본다.
    """

    rule = models.ForeignKey(
        Rule,
        verbose_name=_('규정'),
        related_name='chapters',
        null=True, blank=True)

    parent_chapter = models.ForeignKey(
        'self',
        verbose_name=_('상위챕터'),
        related_name='child_chapters',
        null=True, blank=True,
        on_delete=models.SET_NULL)

    prev_chapter = models.ForeignKey(
        'self',
        verbose_name=_('직전연혁'),
        related_name='next_chapters',
        null=True, blank=True,
        on_delete=models.SET_NULL)

    chapter_type = models.CharField(
        _('종류'),
        max_length=8, choices=get_choices(CHAPTER_TYPE))

    @property
    def chapter_type_v(self):
        return get_verbose(CHAPTER_TYPE, self.chapter_type)

    @chapter_type_v.setter
    def chapter_type_v(self, value):
        self.chapter_type = value

    num = models.IntegerField(
        _('번호'),
        null=True, blank=True)

    content = models.CharField(
        _('내용'),
        max_length=128)

    class Meta:
        verbose_name = '장/절'
        verbose_name_plural = '장/절(들)'

    def __str__(self):
        return "{} {}{}".format(
            self.parent_chapter if self.parent_chapter else self.rule,
            "제{}".format(self.num) if self.num else "",
            get_verbose(CHAPTER_TYPE, self.chapter_type))

    @property
    def d_chapters(self):
        return self.child_chapters.all()

    @property
    def d_articles(self):
        return self.articles.all()

    @property
    def d_clauses(self):
        return self.clauses.filter(
            article=None)

    def get_root_chapter(self):
        if not self.parent_chapter:
            return self
        return self.parent_chapter.get_root_chapter()

    def get_revision_url(self):
        if self.chapter_type == CHAPTER_TYPE['PREAMBLE'][0]:
            return '/revision/preamble'
        if self.chapter_type == CHAPTER_TYPE['CHAPTER'][0]:
            return '/revision/chapter/{}'.format(self.num)
        if self.chapter_type == CHAPTER_TYPE['SECTION'][0]:
            return '/revision/chapter/{}/{}'.format(self.parent_chapter.num, self.num)
        if self.chapter_type == CHAPTER_TYPE['SUPPLEMENT'][0]:
            return '/revision/supplement'
        return '/'

    @property
    def revision_class(self):
        if not self.prev_chapter:
            return 'new'
        if self.prev_chapter.content == self.content:
            prev_clauses = self.prev_chapter.d_clauses
            current_clauses = self.d_clauses
            if len(prev_clauses) != len(current_clauses):
                return 'revised'
            for i in range(len(prev_clauses)):
                if prev_clauses[i].content != current_clauses[i].content:
                    return 'revised'
            return 'maintain'
        return 'revised'

    def get_parents(self):
        if self.parent_chapter:
            return [self.parent_chapter] + self.parent_chapter.get_parents()
        if self.rule:
            return [self.rule]

    def get_rule(self):
        hierarchy = self.get_parents()
        return hierarchy[-1] if hierarchy else None

    @property
    def verbose(self):
        if self.num:
            return _("제{}{} {}").format(
                self.num, get_verbose(CHAPTER_TYPE, self.chapter_type), self.content)
        return self.content


class Article(models.Model):
    """
    조.
    """

    rule = models.ForeignKey(
        Rule,
        verbose_name=_('규정'),
        null=True, blank=True,
        related_name='articles')

    chapter = models.ForeignKey(
        Chapter,
        verbose_name=_('챕터'),
        null=True, blank=True,
        related_name='articles')

    prev_article = models.ForeignKey(
        'self',
        verbose_name=_('직전연혁'),
        related_name='next_article',
        null=True, blank=True,
        on_delete=models.SET_NULL)

    num = models.IntegerField(
        _('번호'))

    title = models.CharField(
        _('제목'),
        max_length=64,
        null=True, blank=True)

    class Meta:
        ordering = ['num']
        verbose_name = '조'
        verbose_name_plural = '조(들)'

    def __str__(self):
        return "{} 제{}조({})".format(self.rule, self.num, self.title)

    @property
    def d_clauses(self):
        return self.clauses.all()

    @property
    def first_clause(self):
        return self.clauses.filter(num=1).first() or (
            self.clauses.all().first())

    @property
    def rest_clauses(self):
        first_clause = self.first_clause
        if not first_clause:
            return self.objects.none()
        return self.clauses.exclude(pk=first_clause.pk)

    @property
    def num_clauses(self):
        return self.clauses.all().count()

    def is_normal(self):
        if self.chapter:
            chapter_type = self.chapter.get_root_chapter().chapter_type
            if chapter_type == CHAPTER_TYPE['PREAMBLE'][0] or (
                    chapter_type == CHAPTER_TYPE['SUPPLEMENT'][0]):
                return False
        return True

    def get_revision_url(self):
        if self.is_normal():
            return '/revision/article/{}'.format(self.num)
        return '/revision/supplement/{}'.format(self.num)

    @property
    def revision_class(self):
        if not self.prev_article:
            return 'new'
        if self.prev_article.title == self.title:
            prev_clauses = self.prev_article.d_clauses
            current_clauses = self.d_clauses
            if len(prev_clauses) != len(current_clauses):
                return 'revised'
            for i in range(len(prev_clauses)):
                if current_clauses[i].content != prev_clauses[i].content:
                    return 'revised'
            return 'maintain'
        return 'revised'

    def get_parents(self):
        if self.chapter:
            return [self.chapter] + self.chapter.get_parents()
        if self.rule:
            return [self.rule]
        return []

    @property
    def verbose(self):
        if self.title:
            return _("제{}조 {}").format(self.num, self.title)
        return _("제{}조").format(self.num)

    def get_rule(self):
        hierarchy = self.get_parents()
        return hierarchy[-1] if hierarchy else None


class Clause(models.Model):
    """
    항.

    여러 항으로 이뤄지지 않고 단일 내용을 담은 조문 역시
    한 개의 항을 갖는 조문으로 본다.

    번호가 없는 항의 경우 최하위 순서로 본다.
    """

    rule = models.ForeignKey(
        Rule,
        related_name='clauses',
        verbose_name=_('규정'),
        null=True, blank=True)

    chapter = models.ForeignKey(
        Chapter,
        related_name='clauses',
        verbose_name=_('챕터'),
        null=True, blank=True)

    article = models.ForeignKey(
        Article,
        related_name='clauses',
        verbose_name=_('조'),
        null=True, blank=True)

    num = models.IntegerField(
        _('번호'),
        null=True, blank=True)

    @property
    def num_v(self):
        if (self.num >= 1 and self.num <= 20):
            return chr(0x245F + self.num)
        return "({})".format(self.num)

    content = models.TextField(
        _('내용'))

    class Meta:
        verbose_name = '항'
        verbose_name_plural = '항(들)'

    def __str__(self):
        return "{} 제{}조 제{}항".format(self.rule, self.article, self.num)

    def get_parents(self):
        if self.article:
            return [self.article] + self.article.get_parents()
        if self.chapter:
            return [self.chapter] + self.chapter.get_parents()
        if self.rule:
            return [self.rule]
        return []

    def get_rule(self):
        hierarchy = self.get_parents()
        return hierarchy[-1] if hierarchy else None
