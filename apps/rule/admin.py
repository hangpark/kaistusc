from django.contrib import admin
from django.db.models import Q
from django import forms

from .models import RuleSet, Rule, Chapter, Article, Clause, Discussion, Comment


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        q = Chapter.objects.exclude(id__exact=self.instance.id)
        rule = self.instance.get_rule()
        if not rule:
            self.fields['parent_chapter'].queryset = q
            self.fields['prev_chapter'].queryset = q
            return
        prev_rule = rule.prev_rule
        q_same_rule = Q(rule=rule) | Q(parent_chapter__rule=rule)
        q_prev_rule = Q(rule=prev_rule) | Q(parent_chapter__rule=prev_rule)
        self.fields['parent_chapter'].queryset = q.filter(q_same_rule)
        self.fields['prev_chapter'].queryset = q.filter(q_prev_rule)


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rule = self.instance.get_rule()
        q = Article.objects.exclude(id__exact=self.instance.id)
        if not rule:
            self.fields['prev_article'].queryset = q
            return
        prev_rule = rule.prev_rule
        q_prev_rule = Q(rule=prev_rule) | Q(chapter__rule=prev_rule) | Q(
            chapter__parent_chapter__rule=prev_rule)
        self.fields['prev_article'].queryset = q.filter(q_prev_rule)
        self.fields['chapter'].queryset = Chapter.objects.filter(
            Q(rule=rule) | Q(parent_chapter__rule=rule))


class ChapterAdmin(admin.ModelAdmin):
    form = ChapterForm


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm

admin.site.register(RuleSet)
admin.site.register(Rule)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Clause)
admin.site.register(Discussion)
admin.site.register(Comment)
