"""
게시판 뷰.
"""
from datetime import date
from datetime import datetime

import os
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers import serialize
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.template.loader import render_to_string
import json

from apps.manager import Custom404
from apps.manager.constants import *
from apps.board.constants import *
from apps.board.forms import BoardBannerForm
from apps.manager.views import ServiceView
from apps.board.constants import *
from django.utils.translation import ugettext_lazy as _

from apps.board.constants_mapping import *

from .models import ACTIVITY_VOTE, Comment, Post, Tag, BoardTab, DebatePost, ProjectPost, AttachedFile, Product, ProductCategory, BoardBanner, Contact


class BoardView(ServiceView):
    """
    특정 게시판 내 게시글 목록 조회 뷰.

    태그와 검색어, 페이지 등이 설정된 경우 이에 맞춰 게시글을 필터링합니다.
    """
    template_name = 'board/board.jinja'

    def dispatch(self, request, *args, **kwargs):
        dispatch = super().dispatch(request, *args, **kwargs)
        # 탭이있을경우 리다이렉트
        board = self.service.board
        tab = kwargs.get('tab', None)
        post = kwargs.get('post', None)
        if not post and not tab and board.boardtab_set.exists() :
            # 포스트와 탭의 경로가아니고, 보드에 탭이있을경우 
            # 첫번째탭으로 리다이렉트
            query = request.META['QUERY_STRING']
            url = self.get_tab(**kwargs).get_absolute_url() + (query and '?' + query)
            return HttpResponseRedirect(url)
        return dispatch
        
    def get_context_data(self, **kwargs):
        """
        게시판 정보를 컨텍스트에 저장하는 메서드.

        게시판, 태그 목록, 검색어, 게시글 목록, 페이지네이션 등을 저장합니다.
        """

        context = super().get_context_data(**kwargs)

        # 상수 저장
        context['BOARD_ROLE'] = BOARD_ROLE
        
        # 게시판 저장
        board = self.service.board
        board.tabs = board.boardtab_set.all()
        context['board'] = board

        # 현재탭 저장
        tab = self.get_tab(**kwargs)
        context['tab'] = tab

        # 현재 위치 저장
        context['current_path'] = tab and tab.get_absolute_url() or board.get_absolute_url()

        # 태그 목록 저장
        context['tags'] = Tag.objects.filter(board=board)
        # 검색어 저장
        search = self.request.GET.get('s')
        context['search'] = search
        filter_state = self.request.GET.get('filter_state')

        # 포스트 모델 설정
        post_model = MAP_MODEL_POST[board.role]
    
        # 게시글 목록 조회
        if (tab):
            post_list = post_model.objects.filter(board=board, board_tab=tab)
        else:
            post_list = post_model.objects.filter(board=board)
        
        if Post in [post_model] + list(post_model.__bases__):
            context['notices'] = post_list.filter(is_notice=True)

        # 태그 필터링
        tag = self.request.GET.get('tag')
        if tag:
            if tag not in [tag.slug for tag in context['tags']]:
                raise Custom404
            post_list = post_list.filter(tag__slug=tag)
        if search:
            if board.check_role(BOARD_ROLE['STORE']):
                post_list = post_list.filter(
                    Q(name__icontains=search) | Q(description__icontains=search))
            else :
                post_list = post_list.filter(is_deleted=False).filter(
                    Q(title__icontains=search) | Q(content__icontains=search))
        
        if filter_state:
            superUser = User.objects.all().filter(is_superuser = True)
            today = datetime.combine(date.today(),datetime.min.time())
            if filter_state == 'finish':
                post_list = post_list.filter(is_deleted=False).filter(Q(is_closed = True)|Q(due_date__lt = today))
            elif filter_state == 'wait':
                post_list = post_list.filter(is_deleted=False ,is_closed = False, due_date__gte = today, vote_up__lte = 2).exclude(author__in = superUser)
            elif filter_state == 'ongoing':
                post_list = post_list.filter(is_deleted=False,is_closed = False, due_date__gte = today).filter(Q(vote_up__gte = 3)|Q(author__in = superUser))
        else:
            filter_state = 'all'
         
        context['filter_state'] = filter_state


        # 상품 목록일 경우
        if self.service.board.check_role(BOARD_ROLE['STORE']):
            # 상품 카테고리 목록 저장
            context['product_categories'] = ProductCategory.objects.all();        
            product_category = self.request.GET.get('product_category')
            if(product_category):
                post_list = post_list.filter(category=product_category)

        # 포스트 리스트 페이지네이션 생성
        context['POST_PER_PAGE'] = POST_PER_PAGE
        paginator = Paginator(post_list, POST_PER_PAGE)
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

        # 보드 배너 저장
        context['board_banner'] = self.get_board_banner(**kwargs)
        
        return context

    def _get_pagination_list(self, page, num_pages):
        if num_pages <= 5:
            return range(1, num_pages + 1)
        pivot = (
            3 * (page < 3) or (num_pages - 2) * (page > num_pages - 2) or page)
        return range(pivot - 2, pivot + 3)

    def get_tab(self,  **kwargs):
        # if self.service.board.exists()
        if (kwargs.get('tab', None)):
            url = kwargs['tab']
            return BoardTab.objects.filter(url=url).first()
        return BoardTab.objects.filter(parent_board=self.service.board).first()
    
    def get_board_banner(self, **kwargs):
        board = self.service.board
        tab = self.get_tab(**kwargs)
        if tab:
            return BoardBanner.objects.filter(board_tab=tab).first()
        else:
            return BoardBanner.objects.filter(board=board).first()


class PostView(BoardView):
    """
    특정 게시글 조회 뷰.

    :class:`BoardView` 를 상속받아 게시판 정보를 자동 저장합니다. 기본
    필요권한이 읽기권한으로 설정되어 있습니다.
    """

    template_name = 'board/post/post.jinja'
    required_permission = PERM_READ

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
        
        post_model = MAP_MODEL_POST[self.service.board.role]
        post = post_model.objects.filter(board=self.service.board, id=kwargs['post']).first()
        
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
        # 페이지네이션 생성
        if not self.service.board.check_role(BOARD_ROLE['CONTACT']):
            # CONTACT의 게시물은 POST 를 기반으로 하지 않습니다.
            comment_list = self.post_.comment_set.all()
            comment_paginator = Paginator(comment_list, COMMENT_PER_PAGE)
            comments = comment_paginator.page(1)
            context['comments'] = comments

            # 게시글에 첨부된 파일 목록 저장
            context['files'] = self.post_.attachedfile_set.all()

        # 게시글에 저장된 스케쥴 저장
        if self.service.board.check_role(BOARD_ROLE['PROJECT']):
            context['schedules'] = self.post_.schedule_set.all()

        return context

class PdfPostView(BoardView):
    """
    최신 pdf 조회 뷰.

    :class:`BoardView` 를 상속받아 게시판 정보를 자동 저장합니다. 기본
    필요권한이 읽기권한으로 설정되어 있습니다.
    """

    template_name = 'board/post/pdf_post.jinja'
    required_permission = PERM_READ

    def has_permission(self, request, *args, **kwargs):
        """
        게시판에 대한 접근권한과 게시글에 대한 필요권한을 체크하는 메서드.

        전역변수 :attr:`post_` 에 게시글 인스턴스가 저장되며, 게시글이 존재하지
        않을 시 404 에러가 발생합니다.
        """
        required_permission = self.required_permission
        self.required_permission = PERM_ACCESS
        kwargs['url'] = kwargs['url'] + '/latest/'
        if not super().has_permission(request, *args, **kwargs):
            return False
        self.required_permission = required_permission
        post = Post.objects.filter(
            board=self.service.board).latest('date')

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

        # 게시글에 첨부된 파일 목록 저장
        context['files'] = self.post_.attachedfile_set.all()
        
        return context


class BoardBannerWriteView(BoardView):
    """
    게시판 배너 등록 뷰.

    기본 필요권한이 쓰기권한으로 설정되어 있습니다.
    """

    required_permission = PERM_WRITE
    template_name = 'board/board_banner_form.jinja'

    def get_context_data(self, **kwargs):
        """
        게시판 배너 작성 폼을 컨텍스트에 추가하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        context['form'] = BoardBannerForm

        return context
    
    def get_redirect_url(self, board_tab):
        return board_tab.get_absolute_url() if board_tab else self.service.get_absolute_url()

    def post(self, request, *args, **kwargs):
        """
        게시판 배너 등록 요청에 따라 게시글을 저장하는 메서드.

        사용자로부터 제출된 게시판 배너 폼을 평가하여 통과될 시 게시판 배너를 
        저장합니다. 올바르지 않은 게시판 배너가 제출된 경우 오류정보를 포함한 폼을
        재전달하여 수정을 요구합니다.
        """
        
        board_banner = BoardBanner(board=self.service.board)
        form = BoardBannerForm(self.service.board, request.POST, instance=board_banner)
        
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.get_redirect_url(form.cleaned_data['board_tab'].first()))
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class BoardBannerEditView(BoardView):

    required_permission = PERM_EDIT
    template_name = 'board/board_banner_form.jinja'
    
    def get_context_data(self, **kwargs):
        """
        게시글 작성 폼을 컨텍스트에 추가하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        board_banner = self.get_board_banner(**kwargs)
        context['board_banner'] = board_banner
        context['form'] = BoardBannerForm

        return context
    
    def get_redirect_url(self, board_tab):
        return board_tab.get_absolute_url() if board_tab else self.service.get_absolute_url()
    
    def post(self, request, *args, **kwargs):
        """
        게시판 배너 수정 요청에 따라 게시글을 업데이트 하는 메서드.

        사용자로부터 제출된 게시판 배너 폼을 평가하여 통과될 시 게시판 배너를
        저장합니다. 올바르지 않은 게시판 배너가 제출된 경우 오류정보를 포함한 폼을
        재전달하여 수정을 요구합니다.
        """
        board_banner = self.get_board_banner(**kwargs)
        form = BoardBannerForm(self.service.board, request.POST, instance=board_banner)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.get_redirect_url(form.cleaned_data['board_tab'].first()))

        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class BoardBannerDeleteView(BoardView):
    """
    게시판 배너 삭제 뷰.

    기본 필요권한이 삭제권한으로 설정되어 있습니다.
    """

    template_name = None
    required_permission = PERM_DELETE

    def post(self, request, *args, **kwargs):
        """
        게시글을 삭제하는 메서드.

        삭제가 완료되면 게시판 메인 페이지로 이동합니다.
        """

        try:
            board_banner = BoardBanner.objects.get(id=kwargs['board_banner_id'])
        except BoardBanner.DoesNotExist:
            return JsonResponse({
                'message': _('존재하지 않는 게시판 배너입니다'),
            }, status=404)
        
        board_banner.delete()
        return JsonResponse({
            'message': _('게시판 배너가 삭제되었습니다'),
        })

class PostWriteView(BoardView):
    """
    게시글 등록 뷰.

    기본 필요권한이 쓰기권한으로 설정되어 있습니다.
    """
        
    required_permission = PERM_WRITE

    # Use this method instead of directly assigning template_name
    def get_template_names(self):
        template_names = ['board/post_form/post_form.jinja']
        if (self.service.board.check_role(BOARD_ROLE['WORKHOUR'])):
            template_names = ['board/post_form/workhour_post_form.jinja']
        elif (self.service.board.check_role(BOARD_ROLE['PLANBOOK'])):
            template_names = ['board/post_form/planbook_post_form.jinja']
        elif (self.service.board.check_role(BOARD_ROLE['CONTACT'])):
            template_names  = ['board/post_form/contact_post_form.jinja']
        return template_names

    def get_context_data(self, **kwargs):
        """
        게시글 작성 폼을 컨텍스트에 추가하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        post_form = MAP_FORM_POST[self.service.board.role]
        context['form'] = post_form(self.service.board)

        return context

    def get_redirect_url(self, post):

        if self.service.board.role in ['PLANBOOK', 'WORKHOUR', 'SPONSOR','CONTACT']:
            return self.service.get_absolute_url()
        else:
            return post.get_absolute_url()

    def post(self, request, *args, **kwargs):
        """
        게시글 등록 요청에 따라 게시글을 저장하는 메서드.

        사용자로부터 제출된 게시글 폼을 평가하여 통과될 시 게시글과 첨부파일을
        저장합니다. 올바르지 않은 게시글이 제출된 경우 오류정보를 포함한 폼을
        재전달하여 수정을 요구합니다.
        """
        user = request.user if request.user.is_authenticated() else None

        board_role = self.service.board.role

        post_model = MAP_MODEL_POST[board_role]
        post_form = MAP_FORM_POST[board_role]
        
        post = post_model(author=user, board=self.service.board)
        form = post_form(self.service.board, request.POST, request.FILES, instance=post)

        if form.is_valid():
            form.save(request.POST, request.FILES)
            return HttpResponseRedirect(self.get_redirect_url(post))
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class PostEditView(PostView):
    """
    게시글 수정 뷰.

    기본 필요권한이 수정권한으로 설정되어 있습니다.
    """

    required_permission = PERM_EDIT

    # Use this method instead of directly assigning template_name
    def get_template_names(self):
        template_names = ['board/post_form/post_form.jinja']
        if (self.service.board.check_role(BOARD_ROLE['WORKHOUR'])):
            template_names = ['board/workhour_form.jinja']
        elif (self.service.board.check_role(BOARD_ROLE['PLANBOOK'])):
            template_names = ['board/planbook_form.jinja']
        elif (self.service.board.check_role(BOARD_ROLE['CONTACT'])):
            template_names  = ['board/post_form/contact_post_form.jinja']
        return template_names

    def get_context_data(self, **kwargs):
        """
        게시글 작성 폼을 컨텍스트에 추가하는 메서드.
        """
        context = super().get_context_data(**kwargs)
        post = self.post_
        post_form = MAP_FORM_POST[self.service.board.role]
        context['form'] = post_form(self.service.board, instance=post)

        return context

    def get_redirect_url(self, post):
        if self.service.board.role in [BOARD_ROLE['PLANBOOK'], BOARD_ROLE['WORKHOUR'], BOARD_ROLE['SPONSOR']]:
            return self.service.get_absolute_url()
        else:
            return post.get_absolute_url()

    def post(self, request, *args, **kwargs):
        """
        게시글 수정 요청에 따라 게시글을 업데이트 하는 메서드.

        사용자로부터 제출된 게시글 폼을 평가하여 통과될 시 게시글과 첨부파일을
        저장합니다. 올바르지 않은 게시글이 제출된 경우 오류정보를 포함한 폼을
        재전달하여 수정을 요구합니다.
        """
        post = self.post_

        post_form = MAP_FORM_POST[self.service.board.role]
        
        form = post_form(self.service.board, request.POST, request.FILES, instance=post)

        if form.is_valid():
            form.save(request.POST, request.FILES)
            return HttpResponseRedirect(self.get_redirect_url(post))
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

class ProductView(BoardView):
    
    template_name = None
    required_permission = PERM_WRITE

    def post(self, request, *args, **kwargs):
        """
        사용자로부터 제출된 상품을 작성하는 메서드.
        작성이 정상적으로 완료되면 작성된 json data를 사용자에게 전달합니다.
        """
        def validate(category_id, price):
            # validate category
            try:
                ProductCategory.objects.get(id=category_id)
            except ProductCategory.DoesNotExist:
                return JsonResponse({
                    'message': _('올바르지 않은 상품카테고리입니다'),
                }, status=400)
            
            # validate price
            if(not price.isdigit()):
                return JsonResponse({
                    'message': _('잘못된 가격 형식입니다'),
                }, status=400)
            return True

        board = self.service.board;
        board_tab = self.get_tab(**kwargs);
        category_id = request.POST.get('category');
        name = request.POST.get('name');
        price = request.POST.get('price');
        description = request.POST.get('description');
        validation = validate(category_id, price)

        #validation
        if(not validation == True):
            return validation

        category = ProductCategory.objects.get(id=category_id)
        price = int(price);
        product = Product.objects.create(
            board=board,
            category=category,
            name=name,
            price=price,
            description=description,
        )
        product.board_tab.add(board_tab)
        return JsonResponse({'product': {
            'category': {
                'id': category.id,
                'name': category.name,
            },
            'name': name,
            'price': price,
            'description': description,
        }})


class ProductDeleteView(BoardView):
    """
    상품 삭제 뷰.

    기본 필요권한이 삭제권한으로 설정되어 있습니다. AJAX 통신에 응답하는
    뷰입니다.
    """
    required_permission = PERM_DELETE

    def post(self, request, *args, **kwargs):
        """
        상품을 삭제하는 메서드.
        """
        try:
            product = Product.objects.get(id=kwargs['product_id'])
        except Product.DoesNotExist:
            return JsonResponse({
                'message': _('존재하지 않는 상품입니다'),
            }, status=404)
        
        product.delete()
        return JsonResponse({
            'message': _('상품이 삭제되었습니다'),
        })


class CommentView(PostView):
    """
    댓글 뷰.

    기본 필요권한이 댓글권한으로 설정되어 있습니다. AJAX 통신에 응답하는
    뷰입니다.
    """

    template_name = 'board/comment.jinja'
    required_permission = PERM_COMMENT

    def get(self, request, *args, **kwargs):
        # 페이지네이션 생성
        comment_list = self.post_.comment_set.all()
        comment_paginator = Paginator(comment_list, COMMENT_PER_PAGE)
        page_num = self.request.GET.get('p')
        comments_page = comment_paginator.page(page_num)
        if comments_page.has_next():
            next_page_num = comments_page.next_page_number()
        else :
            next_page_num = None
        
        comments = [render_to_string('board/comment.jinja', {
            'comment': comment,
            }, request) for comment in comments_page]
        
        return JsonResponse({
            'comments':comments,
            'next_page_num': next_page_num,
        })

    def post(self, request, *args, **kwargs):
        """
        사용자로부터 제출된 댓글을 작성하는 메서드.

        작성이 정상적으로 완료되면 댓글 HTML 소스를 사용자에게 전달합니다.
        """
        user = request.user if request.user.is_authenticated() else None
        comment = Comment.objects.create(
            author=user,
            content=request.POST.get('content'),
            parent_post=self.post_)
        for f in request.FILES.getlist('files'):
            AttachedFile.objects.create(post=comment, file=f)
        context = {'comment': comment}

        return self.render_to_response(self.get_permission_context(context))

class CommentDeleteView(PostView):
    """
    댓글 삭제 뷰.

    기본 필요권한이 삭제권한으로 설정되어 있습니다. AJAX 통신에 응답하는
    뷰입니다.
    """

    template_name = 'board/comment.jinja'
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
        context = {'comment': self.comment}
        return self.render_to_response(self.get_permission_context(context))


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
