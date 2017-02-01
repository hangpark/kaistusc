from django.forms import ModelForm

from .models import AttachedFile, Post


class PostForm(ModelForm):
    """
    포스트를 등록/수정하는 폼.

    ModelForm으로 구현되었으며, save method에서 첨부파일까지 저장한다.
    """

    class Meta:
        model = Post
        fields = (
            'title_ko', 'title_en', 'content_ko', 'content_en',
            'is_notice', 'is_secret', 'tag')

    def save(self, POST, FILES):
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
