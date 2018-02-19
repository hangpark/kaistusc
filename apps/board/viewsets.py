from rest_framework import mixins, viewsets, permissions
from rest_framework.pagination import LimitOffsetPagination

from django.db.models import Q

from apps.board.models import Post
from apps.board.serializers import PostSerializer, CreatePostSerializer, RetrivePostSerializer

from apps.board.constants import POST_PER_PAGE, BOARD_ROLE

class PostPagination(LimitOffsetPagination):
    default_limit = POST_PER_PAGE

class PostViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet
    ):

    permission_classes = (
        permissions.IsAdminUser,
    )
    pagination_class = PostPagination

    def get_queryset(self):
        role = self.request.query_params.get('role', None)
        search = self.request.query_params.get('search', None)
        posts = Post.objects.filter(is_deleted=False)
        if role is not None:
            posts = posts.filter(board__role__exact=role)
        if search is not None:
            posts = posts.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search)
            )
        return posts

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePostSerializer
        elif self.action == 'retrive':
            return RetrivePostSerializer
        else:
            return PostSerializer
