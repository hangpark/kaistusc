from rest_framework import serializers

from apps.board.models import Post, AttachedFile
from apps.manager.constants import PERM_READ


class AttachedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachedFile
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):

    attachedfile_set = AttachedFileSerializer(many=True, read_only=True)
    is_permitted_to_read = serializers.SerializerMethodField()

    def get_request_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

    def get_is_permitted_to_read(self, obj):
        return obj.is_permitted(self.get_request_user(), PERM_READ)

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'content',
            'is_deleted',
            'is_secret',
            'is_permitted_to_read',
            'board',
            'attachedfile_set'
        )
        depth = 2

class RetrivePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'title',
            'content',
            'board',
        )

class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'title',
            'content',
            'board',
        )
