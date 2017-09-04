from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect

from apps.manager.views import ServiceView
from apps.manager.constants import PERM_COMMENT, PERM_DELETE
from .models import RuleSet, Rule, Chapter, Article, Discussion, Comment
from .const import CHAPTER_TYPE


class RuleView(ServiceView):
    """
    특정 규정 조회 뷰.

    규정 세트만 지정되어있고 하위 규정이 지정되지 않은
    경우에는 규정 세트 내 규정 중 가장 최근에 의결된 것을
    기준으로 한다.
    """

    template_name = 'rule/rule.jinja'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 규정 세트 저장
        self.rule_set = self.get_rule_set(**kwargs)
        context['rule_set'] = self.rule_set

        # 규정 저장
        self.rule = self.get_rule(**kwargs)
        context['rule'] = self.rule

        # 규정 연혁 조회
        self.history = self.get_history(**kwargs)
        context['rule_list'] = self.history

        return context

    def get_rule_set(self, **kwargs):
        try:
            if 'rule_set' in kwargs and kwargs['rule_set']:
                return RuleSet.objects.get(slug=kwargs['rule_set'])
            return RuleSet.objects.get(is_main=True)
        except:
            raise Http404

    def get_rule(self, **kwargs):
        if 'revision' in kwargs:
            rule = Rule.objects.filter(
                rule_set=self.rule_set, date_resolved=kwargs['revision']).first()
        else:
            rule = Rule.objects.filter(
                rule_set=self.rule_set).order_by('-date_resolved').first()
        if not rule:
            raise Http404
        return rule

    def get_history(self, **kwargs):
        history = Rule.objects.filter(rule_set=self.rule_set)
        if self.rule.date_resolved:
            history = history.filter(date_resolved__lte=self.rule.date_resolved).order_by(
                '-date_resolved')
        else:
            history = history.exclude(date_resolved=None).order_by('-date_resolved')
        return history


class RevisionView(RuleView):

    def get_service(self, request, *args, **kwargs):
        if 'target' in kwargs:
            kwargs['url'] = '/revision/' + kwargs['target']
        return super().get_service(request, *args, **kwargs)

    def get_rule(self, **kwargs):
        if 'target' in kwargs and kwargs['target'] == 'current':
            rule = Rule.objects.filter(rule_set=self.rule_set).order_by('-date_resolved').first()
        else:
            rule = Rule.objects.filter(rule_set=self.rule_set, date_resolved=None).first()
        if not rule:
            raise Http404
        return rule


class RevisionDiscussionView(RevisionView):
    template_name = 'revision/discussion.jinja'

    def get_service(self, request, *args, **kwargs):
        kwargs['url'] = '/revision/discussion'
        return super().get_service(request, *args, **kwargs)


class RevisionItemView(RevisionDiscussionView):
    rule_item_type = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.rule_item = self.get_target_item(**kwargs)
        self.discussions = self.get_discussion_item()
        context['rule_item'] = self.rule_item
        context['rule_item_type'] = self.rule_item_type
        context['discussions'] = self.discussions
        return context

    def get_target_item(self, **kwargs):
        return super().get_target_item(**kwargs)

    def get_discussion_item(self):
        return super().get_discussion_item()


class RevisionTitleView(RevisionItemView):
    template_name = 'revision/title.jinja'
    rule_item_type = 'title'

    def get_target_item(self, **kwargs):
        return self.rule

    def get_discussion_item(self):
        return Discussion.objects.filter(rule=self.rule)


class RevisionChapterView(RevisionItemView):
    template_name = 'revision/chapter.jinja'
    rule_item_type = 'chapter'

    def get_target_item(self, **kwargs):
        q = Chapter.objects.all()
        if 'type' not in kwargs:
            raise Http404
        elif kwargs['type'] == 'preamble':
            q = q.filter(rule=self.rule, chapter_type=CHAPTER_TYPE['PREAMBLE'][0])
        elif kwargs['type'] == 'supplement':
            q = q.filter(rule=self.rule, chapter_type=CHAPTER_TYPE['SUPPLEMENT'][0])
        elif 'chapter' in kwargs:
            if 'sub_chapter' in kwargs and kwargs['sub_chapter']:
                q = q.filter(chapter_type=CHAPTER_TYPE['SECTION'][0],
                             num=kwargs['sub_chapter'], parent_chapter__num=kwargs['chapter'])
            else:
                q = q.filter(rule=self.rule, chapter_type=CHAPTER_TYPE['CHAPTER'][0],
                             num=kwargs['chapter'])
        else:
            return None
        chapter = q.first()
        if not chapter:
            raise Http404
        return chapter

    def get_discussion_item(self):
        return Discussion.objects.filter(chapter=self.rule_item)


class RevisionArticleView(RevisionItemView):
    template_name = 'revision/article.jinja'
    rule_item_type = 'article'

    def get_target_item(self, **kwargs):
        q = Article.objects.all()
        if 'type' not in kwargs:
            raise Http404
        elif kwargs['type'] == 'supplement':
            q = q.filter(
                chapter__rule=self.rule,
                chapter__chapter_type=CHAPTER_TYPE['SUPPLEMENT'][0],
                num=kwargs['article'])
        elif kwargs['type'] == 'article':
            q = q.filter(
                Q(rule=self.rule) | Q(chapter__rule=self.rule) | Q(
                    chapter__parent_chapter__rule=self.rule),
                Q(chapter=None) | Q(chapter__chapter_type=CHAPTER_TYPE['CHAPTER'][0]) | Q(
                    chapter__chapter_type=CHAPTER_TYPE['SECTION'][0]),
                num=kwargs['article'])
        else:
            return None
        article = q.first()
        if not article:
            raise Http404
        return article

    def get_discussion_item(self):
        return Discussion.objects.filter(article=self.rule_item)


class AddDiscussionView(ServiceView):
    required_permission = PERM_COMMENT

    def get_service(self, request, *args, **kwargs):
        kwargs['url'] = '/revision/discussion'
        return super().get_service(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        rule_item = self.get_rule_item(*args, **kwargs)
        author = request.user if request.user.is_authenticated() else None
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        rule_item_param = {
            'title': 'rule',
            'chapter': 'chapter',
            'article': 'article',
        }
        discussion_param = {
            rule_item_param[kwargs['type']]: rule_item,
            'author': author,
            'subject': subject,
            'from_committee': request.user.is_superuser,
        }
        discussion = Discussion.objects.create(**discussion_param)
        Comment.objects.create(author=author, body=body, discussion=discussion)
        return redirect(discussion.get_rule_item().get_revision_url())

    def get_rule_item(self, *args, **kwargs):
        rule_item_type = {
            'title': Rule,
            'chapter': Chapter,
            'article': Article,
        }
        try:
            rule_item = rule_item_type[kwargs['type']].objects.get(id=kwargs['id'])
        except:
            raise Http404
        return rule_item


class AddCommentView(ServiceView):
    required_permission = PERM_COMMENT

    def has_permission(self, request, *args, **kwargs):
        try:
            self.discussion = Discussion.objects.get(id=kwargs['id'])
        except:
            raise Http404
        if self.discussion.from_committee:
            self.required_permission = PERM_DELETE
        return super().has_permission(request, *args, **kwargs)

    def get_service(self, request, *args, **kwargs):
        kwargs['url'] = '/revision/discussion'
        return super().get_service(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        author = request.user if request.user.is_authenticated() else None
        body = request.POST.get('body')
        Comment.objects.create(
            author=author, body=body, discussion=self.discussion)
        return redirect(self.discussion.get_rule_item().get_revision_url())
