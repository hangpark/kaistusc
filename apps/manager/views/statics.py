"""
고정 페이지 뷰.
"""
from django.db import models
from apps.manager.models import TopBanner
from apps.board.models import Board, BannerCarousel
from apps.board.constants import *
from .base import PageView
from datetime import datetime


class MainPageView(PageView):
    """
    메인페이지 뷰.
    """

    template_name = 'manager/main.jinja'

    def get_context_data(self, **kwargs):
        """
        사용자가 접근 가능한 게시판을 컨텍스트에 전달하는 메서드.

        게시판의 `is_main` 필드가 참인 경우만 필터링하여 저장합니다.
        """
        context = super().get_context_data(**kwargs)
        context['boards'] = Board.objects.accessible_for(
            self.request.user).filter(is_main=True)
        try:
            context['bannerCarousel'] = BannerCarousel.objects.get(sector=BANNER_CAROUSEL_SECTOR['MAIN'])
        except BannerCarousel.DoesNotExist:
            pass
        try:
            context['topBanner'] = TopBanner.objects.get(terminate_at__gte=datetime.now())
        except TopBanner.DoesNotExist:
            pass
        return context


class ErrorView(PageView):
    """
    커스텀 에러페이지 뷰.

    에러 핸들러에 의해 호출되는 뷰입니다. 사이트 네비게이션 기능을 지원하는
    에러페이지를 제작하기 위해 구현되었습니다.
    """

    status_code = 200

    def render_to_response(self, context, **response_kwargs):
        """
        HTTP 응답코드를 전달하는 메서드.
        """
        response_kwargs['status'] = self.status_code
        return super().render_to_response(context, **response_kwargs)
