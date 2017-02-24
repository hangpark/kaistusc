"""
게시판 폼.
"""

from django.forms import ModelForm

from .models import AttachedFile, Post


class PostForm(ModelForm):
    """
    게시글을 등록 및 수정하는 폼.

    :class:`ModelForm`으로 구현되었으며, :meth:`save` 메서드에서 첨부파일까지
    저장합니다.
    """

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
