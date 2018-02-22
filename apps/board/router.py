from rest_framework import routers

from apps.board.viewsets import PostViewSet


router = routers.SimpleRouter()


# PostViewSet

router.register(
    prefix=r'posts',
    base_name='post',
    viewset=PostViewSet,
)
