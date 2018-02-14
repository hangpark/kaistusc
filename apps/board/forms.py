"""
게시판 폼.
"""

from django.forms import ModelForm
import json
from .models import AttachedFile, Post, Tag, BoardTab, ProjectPost, Schedule

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

class ProjectPostForm(PostForm):
    """
    논쟁글을 등록 및 수정하는 폼.

    :class:`POSTForm`으로 구현되었습니다 .
    """

    class Meta:
        model = ProjectPost
        fields = (
            'title_ko', 'title_en', 'content_ko', 'content_en',
            'is_notice', 'is_secret', 'board_tab', 'tag', 'is_pledge',)

    def save(self, POST, FILES):
        """
        사업 게시글과 사업의 스케쥴을 저장하는 메서드.
        """
        post = super().save(POST, FILES)

        schedules = list(map(json.loads, POST.getlist('schedules')))
        prev_schedules = list(filter(lambda schedule: 'id' in schedule, schedules))
        original_schedules = post.schedule_set.all()
        for schedule in original_schedules:
            target_input_schedule = None
            for prev_schedule in prev_schedules:
                if prev_schedule['id'] == schedule.id:
                    target_input_schedule = prev_schedule
                    break
            if not target_input_schedule:
                schedule.delete()
            else:
                schedule.date = prev_schedule['date']
                schedule.save()

        for schedule in filter(lambda schedule: schedule not in prev_schedules, schedules):
            Schedule.objects.create(post=post, title_ko=schedule['title_ko'], title_en=schedule['title_en'], date=schedule['date'])

        return post