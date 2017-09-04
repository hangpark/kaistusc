from django.conf.urls import url

from apps.rule.views import RuleView

urlpatterns = [
    url(r'^(?P<rule_set>\w+)?$', RuleView.as_view()),
    url(r'^(?P<rule_set>\w+)/(?P<revision>\d{4,4}-\d{2,2}-\d{2,2})$', RuleView.as_view()),
]
