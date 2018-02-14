from django.views.generic import FormView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count

from ..forms import TSizeForm
from ..util import vote_available, is_tester
from ..models.club import Club
from ..models.user import Freshman


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(vote_available), name='dispatch')
class TSizeView(FormView):
    template_name = 'tsize.html'
    form_class = TSizeForm
    success_url = '/ot/'

    def form_valid(self, form):
        if hasattr(self.request.user, 'freshman'):
            self.request.user.freshman.tsize = form.cleaned_data['tsize']
            self.request.user.freshman.save()
        else:
            freshman = form.save(commit=False)
            freshman.user = self.request.user
            freshman.save()

        return super(TSizeView, self).form_valid(form)

    def get_initial(self):
        initial = super(TSizeView, self).get_initial()

        if hasattr(self.request.user, 'freshman'):
            initial['tsize'] = self.request.user.freshman.tsize

        return initial


@method_decorator(user_passes_test(is_tester), name='dispatch')
class ResultView(TemplateView):
    template_name = 'result.html'

    def get_context_data(self, **kwargs):
        context = super(ResultView, self).get_context_data(**kwargs)

        context['clubs'] = Club.objects.all().annotate(cnt=Count('votes')).order_by('-cnt')
        context['bands'] = Club.objects.filter(is_band=True).annotate(cnt=Count('votes')).order_by('-cnt')
        context['non_bands'] = Club.objects.filter(is_band=False).annotate(cnt=Count('votes')).order_by('-cnt')

        context['cnt_voted'] = Freshman.objects.all().count()

        # Personal T shirts size
        freshmen = Freshman.objects.all()

        size_list = ""
        for freshman in freshmen:
            info = freshman.user.portal_info
            size_list += "<p>%s,%s,%s</p>" % (info.ku_kname, info.ku_std_no, freshman.tsize)
        context['size_list'] = size_list

        return context
