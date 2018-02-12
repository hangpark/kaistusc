"""
게시판 폼.
"""

from django.forms import ModelForm

from .models import AttachedFile, Post, Tag, DebatePost, Comment


class PostForm(ModelForm):
    """
    게시글을 등록 및 수정하는 폼.

    :class:`ModelForm`으로 구현되었으며, :meth:`save` 메서드에서 첨부파일까지
    저장합니다. 게시글이 속해있는 게시판에서 가능한 태그만 선택할 수 있습니다.
    """

    def __init__(self, board, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tag'].queryset = Tag.objects.filter(board=board)

    class Meta:
        model = Post
        fields = (
            'title_ko', 'title_en', 'content_ko', 'content_en',
            'is_notice', 'is_secret', 'tag')

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


class CommentForm(ModelForm):
    """
    댓글을 등록 및 수정하는 폼.

    :class:`ModelForm`으로 구현되었으며, `save` 메서드에서 첨부파일까지
    저장합니다.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Comment
        fields = ('content',)

    def save(self, POST, FILES):
        """
        게시글과 그에 첨부된 파일들을 저장하는 메서드.
        """
        comment = super().save()
       
        files = FILES.getlist('files')
        for f in files:
            AttachedFile.objects.create(post=comment, file=f)
    
        return comment

class DebateForm(PostForm):
    """
    논쟁글을 등록 및 수정하는 폼.

    :class:`POSTForm`으로 구현되었습니다 .
    """
    
    class Meta:
        model = DebatePost
        fields = (
            'title_ko', 'title_en', 'content_ko', 'content_en',
            'is_notice', 'is_closed','tag', 'due_date', )

