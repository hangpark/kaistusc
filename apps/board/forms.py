from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from .models import Post, AttachedFile


class PostForm(ModelForm):
    """
    포스트를 등록/수정하는 폼.

    ModelForm으로 구현되었으며, save method에서 첨부파일까지 저장한다.
    """

    class Meta:
        model = Post
        fields = ('title', 'content', 'is_notice', 'is_secret', 'tag')

    def save(self, POST, FILES):
        post = super(PostForm, self).save()

        saved_files = POST.getlist('saved_files')
        original_files = post.attachedfile_set.all()
        for f in original_files:
            if str(f.id) not in saved_files:
                f.delete()

        files = FILES.getlist('files')
        for f in files:
            AttachedFile.objects.create(post=post, file=f)
        
        return post
