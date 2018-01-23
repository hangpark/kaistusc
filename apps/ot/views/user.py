from django.views.generic import FormView, View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test

from ..forms import TSizeForm
from ..util import vote_available


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


class MyPageView(View):
    pass