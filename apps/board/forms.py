from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Post, Tag, AttachedFile


class PostForm(forms.Form):

    title = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={
            'placeholder': _("제목"),
        }),
        error_messages={
            'required': _("제목을 입력해주세요."),
            'invalid': _("128자 이내로 입력해주세요."),
        },
    )

    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': _("내용"),
        }),
        error_messages={
            'required': _("내용을 입력해주세요."),
            'invalid': _("내용에 오류가 있습니다."),
        },
    )

    is_notice = forms.BooleanField(
        required=False,
        label=_("공지글"),
    )

    is_secret = forms.BooleanField(
        required=False,
        label=_("비밀글"),
    )

    TAG_CHOICES = tuple(
        [("-1", _("-- 태그 --"))] + [(tag.id, tag) for tag in Tag.objects.all()])
    tag = forms.ChoiceField(
        widget=forms.Select,
        choices=TAG_CHOICES,
    )

    saved_files = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(
            attrs={
                'multiple': True,
            },
        ),
    )

    files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'multiple': True,
            },
        ),
    )

    def clean_tag(self):
        try:
            id = int(self.cleaned_data['tag'])
        except:
            return None
        return Tag.objects.filter(id=id).first()

    def save(self, post=None, board=None, author=None):
        if not post:
            post = Post()
            post.board = board
            post.author = author

        # 포스트 저장
        post.title = self.cleaned_data['title']
        post.content = self.cleaned_data['content']
        post.is_notice = self.cleaned_data['is_notice']
        post.is_secret = self.cleaned_data['is_secret']
        post.tag = self.cleaned_data['tag']
        post.save()

        # 파일 저장
        saved_files = self.data.getlist('saved_files')
        original_files = post.attachedfile_set.all()
        for f in original_files:
            if str(f.id) not in saved_files:
                f.delete()
        files = self.files.getlist('files')
        for f in files:
            AttachedFile.objects.create(post=post, file=f)
        return post
