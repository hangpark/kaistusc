from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from apps.manager.views import BaseServiceView

from .models import Board, Post, Tag


class BoardView(BaseServiceView):
    """
    특정 게시판의 게시글 목록을 보여주는 view.

    태그와 검색어, 페이지 등이 설정된 경우 이에 맞춰 게시글을 필터링한다.
    """

    template_name = 'board/board.jinja'
    
    def get_context_data(self, **kwargs):
        context = super(BoardView, self).get_context_data(**kwargs)

        # Store current board
        board = self.service.board
        context['board'] = board

        # Store tag list
        context['tags'] = Tag.objects.all()

        # Search
        search = self.request.GET.get('s')
        context['search'] = search

        # Fetch post list
        post_list = Post.objects.filter(board=board)
        if kwargs.get('tag', None):
            post_list = post_list.filter(tag__slug=kwargs['tag'])
        if search:
            post_list = post_list.filter(is_deleted=False).filter(
                Q(title__icontains=search) | Q(content__icontains=search))

        # Pagination
        paginator = Paginator(post_list, 15)
        page_num = self.request.GET.get('p')
        try:
            posts = paginator.page(page_num)
        except (PageNotAnInteger, EmptyPage):
            page_num = 1
            posts = paginator.page(page_num)

        # Store page number list
        context['pages'] = self._get_pagination_list(paginator)

        # Store post list
        context['posts'] = posts
        context['notices'] = Post.objects.filter(board=board, is_notice=True)

        return context

    def _get_pagination_list(self, paginator):
        if paginator.num_pages <= 5:
            return range(1, paginator.num_pages + 1)
        pivot = (3 * (page < 3)
            or (paginator.num_pages - 2) * (page > paginator.num_pages - 2)
            or page)
        return range(pivot - 2, pivot + 3)
