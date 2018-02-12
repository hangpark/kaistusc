"""
게시판 뷰.
"""
from datetime import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

from apps.manager import Custom404
from apps.manager.constants import *
from apps.manager.views import ServiceView

from apps.board.constants import *

from .forms import PostForm, CommentForm,DebateForm
from .models import ACTIVITY_VOTE, Comment, Post, Tag,DebatePost

class BoardView(ServiceView):
    """
    특정 게시판 내 게시글 목록 조회 뷰.

    태그와 검색어, 페이지 등이 설정된 경우 이에 맞춰 게시글을 필터링합니다.
    """

    template_name = 'board/board.jinja'

    def get_context_data(self, **kwargs):
        """
        게시판 정보를 컨텍스트에 저장하는 메서드.

        게시판, 태그 목록, 검색어, 게시글 목록, 페이지네이션 등을 저장합니다.
        """
        context = super().get_context_data(**kwargs)

        #게시판 역할 상수 저장
        context['BOARD_ROLE_DEFAULT'] = BOARD_ROLE_DEFAULT
        context['BOARD_ROLE_PROJECT'] = BOARD_ROLE_PROJECT
        context['BOARD_ROLE_DEBATE'] = BOARD_ROLE_DEBATE

        
        # 게시판 저장
        board = self.service.board
        context['board'] = board
        
        
        # 태그 목록 저장
        context['tags'] = Tag.objects.filter(board=board)

        # 검색어 저장
        search = self.request.GET.get('s')
        context['search'] = search
        filter_state = self.request.GET.get('filter_state')

        # 게시글 목록 조회
        if board.check_role(BOARD_ROLE_DEBATE):
            post_list = DebatePost.objects.filter(board=board)
            context['notices'] = DebatePost.objects.filter(board=board, is_notice=True)
        else:
            post_list = Post.objects.filter(board=board)
            context['notices'] = Post.objects.filter(board=board, is_notice=True)
        

        if kwargs.get('tag', None):
            if kwargs['tag'] not in [tag.slug for tag in context['tags']]:
                raise Custom404
            post_list = post_list.filter(tag__slug=kwargs['tag'])
        
        if search:
            post_list = post_list.filter(is_deleted=False).filter(
                Q(title__icontains=search) | Q(content__icontains=search))
        

        if filter_state:
            superUser = User.objects.all().filter(is_superuser = True)
            if filter_state == 'finish':
                post_list = post_list.filter(is_deleted=False).filter(Q(is_closed = True)|Q(due_date__lte = datetime.now()))
            elif filter_state == 'wait':
                post_list = post_list.filter(is_deleted=False ,is_closed = False, due_date__gte = datetime.now(), vote_up__lte = 2).exclude(author__in = superUser)
            elif filter_state == 'debate':
                post_list = post_list.filter(is_deleted=False,is_closed = False, due_date__gte = datetime.now()).filter(Q(vote_up__gte = 3)|Q(author__in = superUser))
        else:
            filter_state = 'all'
         
        context['filter_state'] = filter_state

        # 페이지네이션 생성
        paginator = Paginator(post_list, 15)
        page_num = self.request.GET.get('p')
        try:
            posts = paginator.page(page_num)
        except (PageNotAnInteger, EmptyPage):
            page_num = 1
            posts = paginator.page(page_num)

        # 페이지 번호 목록 저장
        context['pages'] = self._get_pagination_list(
            page_num, paginator.num_pages)

        # 게시글 목록 저장
        context['posts'] = posts
        
        
        return context

    def _get_pagination_list(self, page, num_pages):
        if num_pages <= 5:
            return range(1, num_pages + 1)
        pivot = (
            3 * (page < 3) or (num_pages - 2) * (page > num_pages - 2) or page)
        return range(pivot - 2, pivot + 3)




class PostView(BoardView):
    """
    특정 게시글 조회 뷰.

    :class:`BoardView` 를 상속받아 게시판 정보를 자동 저장합니다. 기본
    필요권한이 읽기권한으로 설정되어 있습니다.
    """
    required_permission = PERM_READ
    template_name = 'board/post.jinja'
    
    def has_permission(self, request, *args, **kwargs):
        """
        게시판에 대한 접근권한과 게시글에 대한 필요권한을 체크하는 메서드.

        전역변수 :attr:`post_` 에 게시글 인스턴스가 저장되며, 게시글이 존재하지
        않을 시 404 에러가 발생합니다.
        """
        required_permission = self.required_permission
        self.required_permission = PERM_ACCESS
        if not super().has_permission(request, *args, **kwargs):
            return False
        self.required_permission = required_permission
        post = Post.objects.filter(
            board=self.service.board, id=kwargs['post']).first()

        if not post:
            raise Http404
        
        self.post_ = post
        return post.is_permitted(request.user, self.required_permission)

    def get(self, request, *args, **kwargs):
        """
        GET 요청이 왔을 시 게시글 조회수를 증가하는 메서드.

        :meth:`has_permission` 을 통과한 사용자에게만 본 메서드가 실행됩니다.
        """
        self.post_.assign_hits(request)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        게시글과 관련 정보를 컨텍스트에 저장하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        # 게시글 저장
        context['post'] = self.post_
        # 게시글에 달린 댓글 목록 저장
        context['comments'] = self.post_.comment_set.all()
        comments_files = {}
        for comment in context['comments']:
            if(comment.attached_file()):
                comments_files[comment.id] = comment.attached_file()
        context['comments_files'] =comments_files

        # 게시글에 첨부된 파일 목록 저장
        context['files'] = self.post_.attachedfile_set.all()

        return context

class DebateView(PostView):

    template_name = 'board/debate/debate.jinja'

    def has_permission(self, request, *args, **kwargs):
        """
        게시판에 대한 접근권한과 게시글에 대한 필요권한을 체크하는 메서드.

        전역변수 :attr:`post_` 에 게시글 인스턴스가 저장되며, 게시글이 존재하지
        않을 시 404 에러가 발생합니다.
        """
        required_permission = self.required_permission
        self.required_permission = PERM_ACCESS
        if not super().has_permission(request, *args, **kwargs):
            return False
        self.required_permission = required_permission
        post = DebatePost.objects.filter(
            board=self.service.board, id=kwargs['post']).first()

        if not post:
            raise Http404
        self.post_ = post
        return post.is_permitted(request.user, self.required_permission)

    def get_context_data(self, **kwargs):
        """
        게시글과 관련 정보를 컨텍스트에 저장하는 메서드.
        """
        context = super().get_context_data(**kwargs)

        # 게시글 저장
        context['post'] = self.post_

        # 게시글에 달린 댓글 목록 저장
        context['comments'] = self.post_.comment_set.all()

        # 게시글에 첨부된 파일 목록 저장
        context['files'] = self.post_.attachedfile_set.all()

        return context


class PostWriteView(BoardView):
    """
    게시글 등록 뷰.

    기본 필요권한이 쓰기권한으로 설정되어 있습니다.
    """
    template_name = 'board/post_form.jinja'
    required_permission = PERM_WRITE

    def get_context_data(self, **kwargs):
        """
        게시글 작성 폼을 컨텍스트에 추가하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(self.service.board)
        return context

    def post(self, request, *args, **kwargs):
        """
        게시글 등록 요청에 따라 게시글을 저장하는 메서드.

        사용자로부터 제출된 게시글 폼을 평가하여 통과될 시 게시글과 첨부파일을
        저장합니다. 올바르지 않은 게시글이 제출된 경우 오류정보를 포함한 폼을
        재전달하여 수정을 요구합니다.
        """
        user = request.user if request.user.is_authenticated() else None
        post = Post(author=user, board=self.service.board)
        print("Post Write View Files ",str(request.FILES))
        form = PostForm(self.service.board, request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save(request.POST, request.FILES)
            return HttpResponseRedirect(post.get_absolute_url())
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class DebateWriteView(BoardView):

    template_name = 'board/debate/debate_form.jinja'
    required_permission = PERM_WRITE

    def get_context_data(self, **kwargs):
        """
        논의 글 작성 폼을 컨텍스트에 추가하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        context['form'] = DebateForm(self.service.board)
        return context

    def post(self, request, *args, **kwargs):
        """
        논의글 등록 요청에 따라 게시글을 저장하는 메서드.

        사용자로부터 제출된 게시글 폼을 평가하여 통과될 시 게시글과 첨부파일을
        저장합니다. 올바르지 않은 게시글이 제출된 경우 오류정보를 포함한 폼을
        재전달하여 수정을 요구합니다.
        """
        user = request.user if request.user.is_authenticated() else None
        post = DebatePost(author=user, board=self.service.board)
        form = DebateForm(self.service.board, request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save(request.POST, request.FILES)
            return HttpResponseRedirect(post.get_absolute_url())
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class PostEditView(PostView):
    """
    게시글 수정 뷰.

    기본 필요권한이 수정권한으로 설정되어 있습니다.
    """

    template_name = 'board/post_form.jinja'
    required_permission = PERM_EDIT

    def get_context_data(self, **kwargs):
        """
        게시글 작성 폼을 컨텍스트에 추가하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        post = self.post_
        context['form'] = PostForm(self.service.board, instance=post)
        return context

    def post(self, request, *args, **kwargs):
        """
        게시글 수정 요청에 따라 게시글을 업데이트 하는 메서드.

        사용자로부터 제출된 게시글 폼을 평가하여 통과될 시 게시글과 첨부파일을
        저장합니다. 올바르지 않은 게시글이 제출된 경우 오류정보를 포함한 폼을
        재전달하여 수정을 요구합니다.
        """
        post = self.post_
        form = PostForm(self.service.board, request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save(request.POST, request.FILES)
            return HttpResponseRedirect(post.get_absolute_url())
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

class DebateEditView(DebateView):
    """
    논의글 수정 뷰
    기본 필요 권한이 수정 권한으로 설정되어 있습니다. 
    """

    template_name = 'board/debate/debate_form.jinja'
    required_permission = PERM_EDIT

    def get_context_data(self, **kwargs):
        """
        게시글 작성 폼을 컨텍스트에 추가하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        post = self.post_
        context['form'] = DebateForm(self.service.board, instance=post)
        return context

    def post(self, request, *args, **kwargs):
        """
        게시글 수정 요청에 따라 게시글을 업데이트 하는 메서드.

        사용자로부터 제출된 게시글 폼을 평가하여 통과될 시 게시글과 첨부파일을
        저장합니다. 올바르지 않은 게시글이 제출된 경우 오류정보를 포함한 폼을
        재전달하여 수정을 요구합니다.
        """
        post = self.post_
        form = DebateForm(self.service.board, request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save(request.POST, request.FILES)
            return HttpResponseRedirect(post.get_absolute_url())
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

class PostDeleteView(PostView):
    """
    게시글 삭제 뷰.

    기본 필요권한이 삭제권한으로 설정되어 있습니다.
    """

    template_name = None
    required_permission = PERM_DELETE

    def post(self, request, *args, **kwargs):
        """
        게시글을 삭제하는 메서드.

        삭제가 완료되면 게시판 메인 페이지로 이동합니다.
        """
        post = self.post_
        post.is_deleted = True
        post.save()
        return HttpResponseRedirect(post.board.get_absolute_url())



class CommentWriteView(PostView):
    """
    댓글 등록 뷰.

    기본 필요권한이 댓글권한으로 설정되어 있습니다. AJAX 통신에 응답하는
    뷰입니다.
    """

    template_name = 'board/comment.jinja'
    required_permission = PERM_COMMENT
   
    def post(self, request, *args, **kwargs):
        """
        사용자로부터 제출된 댓글을 작성하는 메서드.

        작성이 정상적으로 완료되면 댓글 HTML 소스를 사용자에게 전달합니다.
        """
        user = request.user if request.user.is_authenticated() else None
        print('request FILES',str(request))
        comment = Comment.objects.create(
            author=user,
            content=request.POST.get('content'),
            parent_post=self.post_)
        context = {'comment': comment}

        return self.render_to_response(self.get_permission_context(context))


class CommentWriteWithFileView(DebateView):
    """
    첨부 가능한 댓글 등록 뷰.

    기본 필요권한이 댓글권한으로 설정되어 있습니다. AJAX 통신에 응답하는
    뷰입니다.
    """
    template_name = 'board/comment_form.jinja'
    required_permission = PERM_COMMENT
   
    def get_context_data(self, **kwargs):
        """
        댓글 작성 폼을 컨텍스트에 추가하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()

        return context

    def post(self, request, *args, **kwargs):

        """
        댓글 등록 요청에 따라 게시글을 저장하는 메서드.

        사용자로부터 제출된 댓글 폼을 평가하여 통과될 시 게시글과 첨부파일을
        저장합니다. 올바르지 않은 댓글이 제출된 경우 오류정보를 포함한 폼을
        재전달하여 수정을 요구합니다.

        작성이 정상적으로 완료되면 댓글 HTML 소스를 사용자에게 전달합니다.
        """

        user = request.user if request.user.is_authenticated() else None
        
        comment = Comment(author=user, parent_post = self.post_)
        print("Comment Write View Files ",str(request.FILES))

        form = CommentForm(request.POST, request.FILES, instance=comment)

        if form.is_valid():
            form.save(request.POST, request.FILES)
            return HttpResponseRedirect(self.post_.get_absolute_url())
        context = self.get_context_data(**kwargs)
        context['form'] = form
        context = {'comment': comment}
        return self.render_to_response(context)



class CommentDeleteView(PostView):
    """
    댓글 삭제 뷰.

    기본 필요권한이 삭제권한으로 설정되어 있습니다. AJAX 통신에 응답하는
    뷰입니다.
    """

    template_name = None
    required_permission = PERM_DELETE

    def has_permission(self, request, *args, **kwargs):
        """
        포스트에 대한 읽기권한과 댓글에 대한 필요권한을 체크하는 메서드.

        전역변수 :attr:`comment` 에 댓글 인스턴스가 저장되며, 댓글이 존재하지
        않을 시 404 에러가 발생합니다.
        """
        required_permission = self.required_permission
        self.required_permission = PERM_READ
        if not super().has_permission(request, *args, **kwargs):
            return False
        self.required_permission = required_permission
        comment = Comment.objects.filter(
            parent_post__board=self.service.board,
            parent_post__id=kwargs['post'],
            id=kwargs['comment']).first()

        if not comment:
            raise Http404
        self.comment = comment
        return comment.is_permitted(request.user, self.required_permission)

    def post(self, request, *args, **kwargs):
        """
        댓글을 삭제하는 메서드.
        """
        self.comment.is_deleted = True
        self.comment.save()
        return HttpResponse()


class PostVoteView(PostView):
    """
    게시글 추천/비추천 활동을 처리하는 뷰.

    기본 필요권한이 읽기권한으로 설정되어 있습니다. AJAX 통신에 응답하는
    뷰입니다.
    """

    required_permission = PERM_READ

    def has_permission(self, request, *args, **kwargs):
        """
        기본 필요권한에 더해 로그인 여부를 체크하는 메서드.

        로그인이 되어있지 않은 경우에는 추천/비추천 기능을 이용할 수 없게 만드는
        메서드입니다.
        """
        if not super().has_permission(request, *args, **kwargs):
            return False
        return request.user.is_authenticated

    def post(self, request, *args, **kwargs):
        """
        URL로 전달된 모드에 맞게 추천 또는 비추천 처리를 하는 메서드.
        """
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
