"""
게시판 폼.
"""

from django.forms import ModelForm
import json
from django.conf import settings
from dateutil.parser import parse

from .models import (
    BoardBanner, BoardTab,
    Post, DebatePost, ProjectPost, 
    AttachedFile, Tag, Schedule, WebDoc, 
    Comment, Contact
)

import pytz

class BoardBannerForm(ModelForm):
    """
    게시판 배너를 등록 및 수정하는 폼.

    :class:`ModelForm`으로 구현되었습니다.
    """

    def __init__(self, board, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['board_tab'].queryset = BoardTab.objects.filter(parent_board=board)

    class Meta:
        model = BoardBanner
        fields = (
            'text', 'url', 'board_tab'
        )
    

class PostForm(ModelForm):
    """
    게시글을 등록 및 수정하는 폼.

    :class:`ModelForm`으로 구현되었으며, :meth:`save` 메서드에서 첨부파일까지
    저장합니다. 게시글이 속해있는 게시판에서 가능한 태그만 선택할 수 있습니다.
    """

    def __init__(self, board, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['board_tab'].queryset = BoardTab.objects.filter(parent_board=board)
        self.fields['tag'].queryset = Tag.objects.filter(board=board)

    class Meta:
        model = Post
        fields = (
            'title_ko', 'title_en', 'content_ko', 'content_en',
            'is_notice', 'is_secret', 'board_tab', 'tag')

    def save(self, POST, FILES):
        """
        게시글과 그에 첨부된 파일들을 저장하는 메서드.
        """
        post = super().save()

        prev_files = POST.getlist('prev_files')
        original_files = post.attachedfile_set.all()
        for f in original_files:
            if str(f.id) not in prev_files:
                f.delete()

        files = FILES.getlist('files')
        for f in files:
            AttachedFile.objects.create(post=post, file=f)

        return post

class DebatePostForm(PostForm):
    class Meta:
        model = DebatePost
        fields = (
            'title_ko', 'title_en', 'content_ko', 'content_en',
            'is_notice', 'is_closed','tag', 'board_tab', )
    def save(self, POST, FILES):
        post = super().save(POST, FILES)
        post.due_date = parse_date_string(POST['due_date'])
        post.save()
        return post

class WorkhourPostForm(PostForm):
    class Meta:
        model = Post
        fields = (
            'title_ko', 'title_en', 'content_ko', 'content_en',
            'is_notice', 'tag', 'board_tab', 'is_secret')
    
    def sanitize(self, POST):
        POST['embed_url'] = POST['embed_url'].replace('/edit', '/preview')
        
    def save(self, POST, FILES):
        post = super().save(POST, FILES)
        webdocs = post.webdoc_set.all()

        self.sanitize(POST)

        if webdocs:
            webdocs[0].embed_url = POST['embed_url']
        else:
            WebDoc.objects.create(post=post, embed_url=POST['embed_url'])

        post.title_ko = post.board.role
        post.save()
        return post

class PlanbookPostForm(PostForm):
    class Meta:
        model = Post
        fields = (
            'title_ko', 'title_en', 'content_ko', 'content_en',
            'is_notice', 'tag', 'board_tab', 'is_secret')
    def save(self, POST, FILES):
        post = super().save(POST, FILES)

        post.title_ko = post.board.role
        post.content_ko = post.board.role
        post.save()
        return post

class ProjectPostForm(PostForm):
    """
    진행중인 사업을 등록 및 수정하는 폼.

    :class:`POSTForm`으로 구현되었습니다 .
    """
    
    class Meta:
        model = ProjectPost
        fields = (
            'title_ko', 'title_en', 'content_ko', 'content_en',
            'is_notice', 'is_secret', 'board_tab', 'tag', 'is_pledge',)

    def save(self, POST, FILES):
        """
        사업 게시글과 사업의 스케줄을 저장하는 메서드.
        schedule의 데이터가 'request.POST'의 'schedules' 에 저장되어있습니다
        기존 post의 schedule_set과 비교하여
        - 없으면 -> 삭제
        - 날짜가 수정되었으면 -> 수정
        - 신규 schedule이면 -> 생성
        """
        post = super().save(POST, FILES)

        schedules = list(map(json.loads, POST.getlist('schedules')))
        prev_schedules = list(filter(lambda schedule: 'id' in schedule, schedules))
        original_schedules = post.schedule_set.all()
        for schedule in original_schedules:
            target_input_schedule = next((s for s in prev_schedules if s['id'] == schedule.id), None)
            if not target_input_schedule: # 기존 스케줄 삭제
                schedule.delete()
            else: # 기존 스케줄 날짜 수정
                schedule.date = parse_date_string(target_input_schedule['date'])
                schedule.save()

        for schedule in filter(lambda s: s not in prev_schedules, schedules): # 새 스캐줄 생성
            Schedule.objects.create(
                post=post,
                title_ko=schedule['title_ko'],
                title_en=schedule['title_en'],
                date=parse_date_string(schedule['date']),
            )

        return post


class ContactForm(ModelForm):
    """
    각 산하기구의 연락처 모델을 저장하는 폼입니다.
    :class:`ModelForm`으로 구현되었으며, :meth:`save` 메서드에서 첨부파일까지
    저장합니다. 
    """
    def __init__(self, board, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['board_tab'].queryset = BoardTab.objects.filter(parent_board=board)

    class Meta:
        model = Contact;
        fields = (
            'name_ko','name_en','content_ko', 'content_en', 'board_tab','phone','url', )

    def save(self, POST, FILES):
        """
        게시글과 그에 첨부된 파일들을 저장하는 메서드.
        """
        contact = super().save()
        return contact



def parse_date_string(date_string):
    local_time_zone = pytz.timezone(settings.TIME_ZONE)
    date = parse(date_string)
    if(date.tzinfo is None):
        return date
    return date.astimezone(local_time_zone).replace(tzinfo=None)
