from django.contrib.auth.models import AnonymousUser, Group, User
from django.test import TestCase

from apps.manager.models import *

from .models import *


class BoardTestCase(TestCase):
    def setUp(self):
        """
                  |  board_all    board_log    board_grp1   board_grp2   board_cls
        ----------+---------------------------------------------------------------------
        anon      |  Accessible   None         None         None         None
                  |
        usr1      |  Accessible   Writable     Editable     Readable     None(Readable)
                  |
        usr2      |  Accessible   Writable     Editable     Deletable    None(Deletable)
                  |
        superuser |  Deletable    Deletable    Deletable    Deletable    Deletable
        """

        # 카테고리 생성
        self.cat = Category.objects.create(
            name='Test Category'
        )

        # 게시판 생성
        self.board_all = Board.objects.create(
            name='Board for all users',
            category=self.cat,
            max_permission_anon=PERMISSION_ACCESSIBLE,
            max_permission_auth=PERMISSION_NONE
        )
        self.board_log = Board.objects.create(
            name='Board for logged in users',
            category=self.cat,
            max_permission_anon=PERMISSION_NONE,
            max_permission_auth=PERMISSION_WRITABLE
        )
        self.board_grp1 = Board.objects.create(
            name='Board for groups #1',
            category=self.cat,
            max_permission_anon=PERMISSION_NONE,
            max_permission_auth=PERMISSION_NONE
        )
        self.board_grp2 = Board.objects.create(
            name='Board for groups #2',
            category=self.cat,
            max_permission_anon=PERMISSION_NONE,
            max_permission_auth=PERMISSION_NONE
        )
        self.board_cls = Board.objects.create(
            name='Board closed',
            category=self.cat,
            max_permission_anon=PERMISSION_WRITABLE,
            max_permission_auth=PERMISSION_DELETABLE,
            is_closed=True
        )

        # 유저 생성
        self.anon = AnonymousUser()
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

        # 유저를 그룹에 배정시킨다.
        self.user1.groups.add(self.grp1)
        self.user2.groups.add(self.grp1)
        self.user2.groups.add(self.grp2)

        # 게시판 이용권한 설정
        GroupServicePermission.objects.create(
            group=self.grp1,
            service=self.board_grp1,
            permission=PERMISSION_EDITABLE
        )
        GroupServicePermission.objects.create(
            group=self.grp1,
            service=self.board_grp2,
            permission=PERMISSION_READABLE
        )
        GroupServicePermission.objects.create(
            group=self.grp2,
            service=self.board_grp2,
            permission=PERMISSION_DELETABLE
        )
        GroupServicePermission.objects.create(
            group=self.grp1,
            service=self.board_cls,
            permission=PERMISSION_READABLE
        )
        GroupServicePermission.objects.create(
            group=self.grp2,
            service=self.board_cls,
            permission=PERMISSION_DELETABLE
        )

    def test_board_permission_for_various_types_of_user(self):
        """
        서비스의 퍼미션과 유저 상태에 따라 접근가능한지 여부를 체크한다.
        """

        # 각 유저의 접근가능 보드를 구한다.
        qs = Board.objects.order_by('pk')
        res_anon = qs.accessible_for(self.anon)
        res_user1 = qs.accessible_for(self.user1)
        res_user2 = qs.accessible_for(self.user2)
        res_superuser = qs.accessible_for(self.superuser)

        # 접근가능 게시판 목록 결과 테스트
        self.assertQuerysetEqual(res_anon, map(repr, [
            self.board_all]))

        self.assertQuerysetEqual(res_user1, map(repr, [
            self.board_all, self.board_log, self.board_grp1, self.board_grp2]))

        self.assertQuerysetEqual(res_user2, map(repr, [
            self.board_all, self.board_log, self.board_grp1, self.board_grp2]))

        self.assertQuerysetEqual(res_superuser, map(repr, [
            self.board_all, self.board_log, self.board_grp1,
            self.board_grp2, self.board_cls]))


        def test_board_permission(permission, exp_res):
            users = [self.anon, self.user1, self.user2, self.superuser]
            boards = [
                self.board_all, self.board_log, self.board_grp1,
                self.board_grp2, self.board_cls]
            res = [(repr(user), repr(board), board.is_permitted(user, permission))
            for user in users for board in boards]

            temp_list = [[repr(user), repr(board)]
                for user in users for board in boards]
            self.assertEqual(res, [
                (e[0], e[1], exp_res[i]) for i, e in enumerate(temp_list)])

        test_board_permission(PERMISSION_ACCESSIBLE, [
            True, False, False, False, False,
            True, True, True, True, False,
            True, True, True, True, False,
            True, True, True, True, True])

        test_board_permission(PERMISSION_READABLE, [
            False, False, False, False, False,
            False, True, True, True, False,
            False, True, True, True, False,
            True, True, True, True, True])

        test_board_permission(PERMISSION_COMMENTABLE, [
            False, False, False, False, False,
            False, True, True, False, False,
            False, True, True, True, False,
            True, True, True, True, True])

        test_board_permission(PERMISSION_WRITABLE, [
            False, False, False, False, False,
            False, True, True, False, False,
            False, True, True, True, False,
            True, True, True, True, True])

        test_board_permission(PERMISSION_EDITABLE, [
            False, False, False, False, False,
            False, False, True, False, False,
            False, False, True, True, False,
            True, True, True, True, True])

        test_board_permission(PERMISSION_DELETABLE, [
            False, False, False, False, False,
            False, False, False, False, False,
            False, False, False, True, False,
            True, True, True, True, True])
    
    def test_post_permission(self):
        self.post_normal = Post.objects.create(
            author=self.user2,
            board=self.board_grp2,
            title="Post Normal",
            content="post normal")
        self.post_secret = Post.objects.create(
            author=self.user2,
            board=self.board_grp2,
            title="Post Secret",
            content="post secret",
            is_secret=True)
        self.post_deleted = Post.objects.create(
            author=self.user2,
            board=self.board_grp2,
            title="Post Deleted",
            content="post deleted",
            is_deleted=True)

        def test_post_permission(permission, exp_res):
            users = [self.anon, self.user1, self.user2, self.superuser]
            posts = [self.post_normal, self.post_secret, self.post_deleted]
            res = [(repr(user), repr(post), post.is_permitted(user, permission))
            for user in users for post in posts]

            temp_list = [[repr(user), repr(post)]
                for user in users for post in posts]
            self.assertEqual(res, [
                (e[0], e[1], exp_res[i]) for i, e in enumerate(temp_list)])

        test_post_permission(PERMISSION_READABLE, [
            False, False, False,
            True, False, False,
            True, True, False,
            True, True, True
        ])
        test_post_permission(PERMISSION_COMMENTABLE, [
            False, False, False,
            False, False, False,
            True, True, False,
            True, True, True
        ])
        test_post_permission(PERMISSION_EDITABLE, [
            False, False, False,
            False, False, False,
            True, True, False,
            True, True, True
        ])
        test_post_permission(PERMISSION_DELETABLE, [
            False, False, False,
            False, False, False,
            True, True, False,
            True, True, True
        ])
