from rest_framework import mixins, viewsets, permissions

from apps.board.models import Post
from apps.board.serializers import PostSerializer


class PostViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
