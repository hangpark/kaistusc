from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from .models import PortalInfo


def portal_info_protection(func):
    """
    유저 리스트에서 정보제공 미동의 유저의 포탈 계정정보를 출력하지 않도록
    처리하는 데코레이터
    """

    def decorator(self, e):
        if not e.portal_info.is_signed_up:
            raise ObjectDoesNotExists
        return func(self, e)
    return decorator


class PortalInfoInline(admin.StackedInline):
    """
    유저 모델 인스턴스 수정 시 포탈 계정정보 동시 수정을 위한 인라인
    """

    model = PortalInfo
    verbose_name = _('포탈 계정정보')
    verbose_name_plural = _('포탈 계정정보(들)')


class CustomUserAdmin(UserAdmin):
    """
    유저 모델과 포탈 계정정보를 연동한 커스텀 어드민
    """
    
    inlines = [PortalInfoInline] + UserAdmin.inlines

    fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Permissions'), {'fields': (('is_staff', 'is_superuser'), 'groups')}),
    )
    
    list_display = (
        'portal_name',
        'portal_std_no',
        'portal_prog',
        'portal_dept',
        'portal_status',
        'portal_sex',
        'portal_born_date',
        'portal_mobile',
        'portal_mail',
    )

    list_filter = (
        'is_staff',
        'portal_info__ku_acad_prog',
        'portal_info__ku_psft_user_status_kor',
        'portal_info__ku_sex',
    )

    search_fields = (
        'username',
        'portal_info__ku_kname',
        'portal_info__ku_std_no',
        'portal_info__mobile',
    )

    ordering = ('is_staff', 'portal_info__ku_kname', 'username')

    def portal_name(self, e):
        try:
            name = e.portal_info.ku_kname
        except:
            name = "(*) " + e.username
        return name
    portal_name.short_description = _('이름')

    @portal_info_protection
    def portal_std_no(self, e):
        return e.portal_info.ku_std_no
    portal_std_no.short_description = _('학번')

    @portal_info_protection
    def portal_prog(self, e):
        return e.portal_info.ku_acad_prog
    portal_prog.short_description = _('과정')

    @portal_info_protection
    def portal_dept(self, e):
        return e.portal_info.ou
    portal_dept.short_description = _('학과')

    @portal_info_protection
    def portal_status(self, e):
        return e.portal_info.ku_psft_user_status_kor
    portal_status.short_description = _('학적상태')

    @portal_info_protection
    def portal_sex(self, e):
        return e.portal_info.ku_sex
    portal_sex.short_description = _('성별')

    @portal_info_protection
    def portal_born_date(self, e):
        return e.portal_info.ku_born_date
    portal_born_date.short_description = _('생년월일')

    @portal_info_protection
    def portal_mobile(self, e):
        return e.portal_info.mobile
    portal_mobile.short_description = _('전화번호')

    @portal_info_protection
    def portal_mail(self, e):
        return e.portal_info.mail
    portal_mail.short_description = _('메일주소')


class UserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    그룹멤버 설정 시 유저 리스트 출력 방식
    """

    def label_from_instance(self, obj):
        try:
            name = "%s (%s, %s, %s, %s)" % (
                obj.portal_info.ku_kname,
                obj.portal_info.ku_std_no,
                obj.portal_info.ku_acad_prog,
                obj.portal_info.ku_born_date,
                obj.portal_info.ou,
            )
        except:
            name = "(*) " + obj.username
        return name


class GroupAdminForm(forms.ModelForm):
    """
    그룹멤버 설정 폼
    """

    users = UserModelMultipleChoiceField(
        label=_('그룹멤버'),
        queryset = User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name = _('유저(들)'),
            is_stacked = False
        ),
    )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    class Meta:
        model = Group
        fields = '__all__'

    def save(self, commit=True):
        group = super(GroupAdminForm, self).save(commit=False)
        if commit:
            group.save()
        if group.pk:
            group.user_set = self.cleaned_data['users']
            self.save_m2m()
        return group


class CustomGroupAdmin(admin.ModelAdmin):
    """
    그룹 설정 커스텀 어드민
    """

    form = GroupAdminForm
    fieldsets = (
        (None, {'fields': ('name', 'users')}),
    )


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
