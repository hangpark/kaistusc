from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import render
from apps.manager.models import Service
from apps.manager.constants import *
from apps.manager.views import BaseServiceView
from django.http import Http404, HttpResponse, HttpResponseRedirect
from .forms import PostForm
from .models import Board, Post, Tag, Comment, PostActivity, ACTIVITY_VOTE


class BoardView(BaseServiceView):
    """
    특정 게시판의 게시글 목록을 보여주는 view.

    태그와 검색어, 페이지 등이 설정된 경우 이에 맞춰 게시글을 필터링한다.
    """

    template_name = 'board/board.jinja'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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


class PostView(BoardView):
    """
    특정 포스트 내용을 보는 view.
    """

    template_name = 'board/post.jinja'
    required_permission = PERM_READ

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        self.post_.assign_hits(request)
        return response

    def has_permission(self, request, *args, **kwargs):
        required_permission = self.required_permission
        self.required_permission = PERM_ACCESS
        if not super().has_permission(request, *args, **kwargs):
            return False
        self.required_permission = required_permission
        post = Post.objects.filter(board=self.service.board, id=kwargs['post']).first()

        if not post:
            raise Http404
        self.post_ = post
        return post.is_permitted(request.user, self.required_permission)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Store current post
        context['post'] = self.post_

        # Store comments for current post
        context['comments'] = self.post_.comment_set.all()

        # Store attached files for current post
        context['files'] = self.post_.attachedfile_set.all()

        return context


class PostWriteView(BoardView):
    """
    새로운 포스트를 등록하는 view.
    """

    template_name = 'board/post_form.jinja'
    required_permission = PERM_WRITE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated() else None
        post = Post(author=user, board=self.service.board)
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save(request.POST, request.FILES)
            return HttpResponseRedirect(post.get_absolute_url())
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class PostEditView(PostView):
    """
    특정 포스트를 수정하는 view.
    """

    template_name = 'board/post_form.jinja'
    required_permission = PERM_EDIT

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.post_
        context['form'] = PostForm(instance=post)
        return context

    def post(self, request, *args, **kwargs):
        post = self.post_
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save(request.POST, request.FILES)
            return HttpResponseRedirect(post.get_absolute_url())
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class PostDeleteView(PostView):

    template_name = None
    required_permission = PERM_DELETE

    def post(self, request, *args, **kwargs):
        post = self.post_
        post.is_deleted = True
        post.save()
        return HttpResponseRedirect(post.board.get_absolute_url())


class CommentWriteView(PostView):

    template_name = 'board/comment.jinja'
    required_permission = PERM_COMMENT

    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated() else None
        comment = Comment.objects.create(
            author=user,
            content=request.POST.get('content'),
            parent_post=self.post_)
        context = {'comment': comment}
        return self.render_to_response(self.get_permission_context(context))


class CommentDeleteView(PostView):

    template_name = None
    required_permission = PERM_DELETE

    def has_permission(self, request, *args, **kwargs):
        if not super().has_permission(request, *args, **kwargs):
            return False
        comment = Comment.objects.filter(
            parent_post__board=self.service.board,
            parent_post__id=kwargs['post'],
            id=kwargs['comment']).first()

        if not comment:
            raise Http404
        self.comment = comment
        return comment.is_permitted(request.user, self.required_permission)

    def post(self, request, *args, **kwargs):
        self.comment.is_deleted = True
        self.comment.save()
        return HttpResponse()


class PostVoteView(PostView):

    required_permission = PERM_READ

    def has_permission(self, request, *args, **kwargs):
        if not super().has_permission(request, *args, **kwargs):
            return False
        return request.user.is_authenticated

    def post(self, request, *args, **kwargs):
        post = self.post_
        if not ('mode' in kwargs and kwargs['mode'] in ['up', 'down']):
            raise Http404
        is_new = post.assign_activity(request, ACTIVITY_VOTE)
        if is_new:
            if kwargs['mode'] == 'up':
                post.vote_up += 1
            if kwargs['mode'] == 'down':
                post.vote_down += 1
            post.save()
        return HttpResponse(is_new)
