from django.contrib import admin

from .models import RuleSet, Rule, Chapter, Article, Clause, Discussion, Comment

admin.site.register(RuleSet)
admin.site.register(Rule)
admin.site.register(Chapter)
admin.site.register(Article)
admin.site.register(Clause)
admin.site.register(Discussion)
admin.site.register(Comment)
