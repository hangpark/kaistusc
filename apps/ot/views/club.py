from django.views.generic import ListView, DetailView
from django.http import Http404
from django.shortcuts import redirect

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from ..models.club import Club
from ..util import vote_available


class ClubListView(ListView):
    template_name = 'club_list.html'
    context_object_name = 'clubs'

    def get_queryset(self):
        if 'is_band' in self.request.GET:
            if self.request.GET['is_band'] == '0':
                queryset = Club.objects.filter(is_band=False)
            elif self.request.GET['is_band'] == '1':
                queryset = Club.objects.filter(is_band=True)
            else:
                raise Http404
        else:
            queryset = Club.objects.all()

        return queryset.order_by('?')


class ClubDetailView(DetailView):
    template_name = 'club_detail.html'
    model = Club

    def get_context_data(self, **kwargs):
        context = super(ClubDetailView, self).get_context_data(**kwargs)

        user = self.request.user
        available = vote_available(user)
        context['available'] = available

        if hasattr(user, 'freshman'):
            club = self.object

            # 유저가 이미 해당 동아리에 투표했는지 여부
            context['voted'] = bool(user.freshman.voted_clubs.filter(pk=club.pk))
            # 유저가 해당 동아리 계열(밴드/비밴드) 최대 투표수를 넘었는지 여부
            context['exceeded'] = user.freshman.vote_limit_exceeded(club.is_band)

        return context

    @method_decorator(login_required())
    def post(self, request, *args, **kwargs):
        """
        현재 동아리에 투표
        """
        if vote_available(request.user):
            club = self.get_object()
            freshman = request.user.freshman

            voted = freshman.voted_clubs.filter(pk=club.pk)

            if voted:
                freshman.voted_clubs.remove(club)
                freshman.save()
            elif not freshman.vote_limit_exceeded(club.is_band):
                freshman.voted_clubs.add(club)
                freshman.save()

        return redirect('.')
