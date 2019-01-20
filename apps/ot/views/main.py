from django.views.generic import TemplateView
from ..util import vote_available
from ..models.user import Freshman


class MainView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)

        context['available'] = vote_available(self.request.user)

        if hasattr(self.request.user, 'freshman'):
            voted_clubs = self.request.user.freshman.voted_clubs
            context['voted_band'] = voted_clubs.filter(is_band=True)
            context['voted_non_band'] = voted_clubs.filter(is_band=False)
        else:
            context['voted_band'] = []
            context['voted_non_band'] = []

        context['band_limit'] = Freshman.BAND_VOTE_LIMIT
        context['non_band_limit'] = Freshman.NON_BAND_VOTE_LIMIT
        context['total_limit'] = Freshman.BAND_VOTE_LIMIT + Freshman.NON_BAND_VOTE_LIMIT

        return context

    def post(self, request, *args, **kwargs):
        pass

