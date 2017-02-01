from apps.board.models import Board

from .base import PageView


class MainPageView(PageView):
    """
    메인 페이지 view.

    유저가 접근 가능한 공개게시판의 글을 확인한다.
    """

    template_name = 'manager/main.jinja'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boards'] = Board.objects.accessible_for(
            self.request.user).filter(is_main=True)
        return context


class ErrorView(PageView):
    """
    에러 뷰
    """

    status_code = 200

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['status'] = self.status_code
        return super().render_to_response(context, **response_kwargs)
