from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser, Group
from .models import *

class ServiceTestCase(TestCase):
    def setUp(self):
        # 카테고리 생성
        self.cat = Category.objects.create(
            name='Category #1'
        )

        # 서비스 생성
        self.svc_all = Service.objects.create(
            name='Service for all users',
            category=self.cat,
            permission = PERMISSION_ALL_USERS
        )
        self.svc_log = Service.objects.create(
            name='Service for logged in users',
            category=self.cat,
            permission = PERMISSION_LOGGED_IN_USERS
        )
        self.svc_grp1 = Service.objects.create(
            name='Service for accessible groups #1',
            category=self.cat,
            permission = PERMISSION_ACCESSIBLE_GROUPS
        )
        self.svc_grp2 = Service.objects.create(
            name='Service for accessible groups #2',
            category=self.cat,
            permission = PERMISSION_ACCESSIBLE_GROUPS
        )
        self.svc_cls = Service.objects.create(
            name='Service closed',
            category=self.cat,
            permission = PERMISSION_CLOSED
        )

        # 유저 생성
        self.user1 = User.objects.create(
            username='User #1',
            email='user1@test.com',
            password='pwd_user1'
        )
        self.user2 = User.objects.create(
            username='User #2',
            email='user2@test.com',
            password='pwd_user2'
        )
        self.superuser = User.objects.create_superuser(
            username='Superuser',
            email='root@test.com',
            password='root'
        )

        # 그룹 생성
        self.grp1 = Group.objects.create(
            name='Group #1'
        )
        self.grp2 = Group.objects.create(
            name='Group #2'
        )

    def test_service_permission_for_various_types_of_user(self):
        """
        서비스의 퍼미션과 유저 상태에 따라 접근가능한지 여부를 체크한다.
        """
        # 유저를 그룹에 배정시킨다.
        self.user1.groups.add(self.grp1)
        self.user2.groups.add(self.grp1)
        self.user2.groups.add(self.grp2)

        # 그룹에게 서비스 접근권한을 부여한다.
        GroupServicePermission.objects.create(
                group=self.grp2, service=self.svc_all)
        GroupServicePermission.objects.create(
                group=self.grp2, service=self.svc_log)
        GroupServicePermission.objects.create(
                group=self.grp1, service=self.svc_grp1)
        GroupServicePermission.objects.create(
                group=self.grp2, service=self.svc_grp2)
        GroupServicePermission.objects.create(
                group=self.grp2, service=self.svc_cls)

        # 각 유저의 이용가능 서비스를 구한다.
        qs = Service.objects.order_by('pk')
        res_anon = qs.available_for(AnonymousUser())
        res_user1 = qs.available_for(self.user1)
        res_user2 = qs.available_for(self.user2)
        res_superuser = qs.available_for(self.superuser)

        # 결과 테스트
        self.assertQuerysetEqual(res_anon, map(repr, [
            self.svc_all]))

        self.assertQuerysetEqual(res_user1, map(repr, [
            self.svc_all, self.svc_log, self.svc_grp1]))

        self.assertQuerysetEqual(res_user2, map(repr, [
            self.svc_all, self.svc_log, self.svc_grp1, self.svc_grp2]))

        self.assertQuerysetEqual(res_superuser, map(repr, [
            self.svc_all, self.svc_log, self.svc_grp1,
            self.svc_grp2, self.svc_cls]))
