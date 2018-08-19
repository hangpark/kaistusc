from rest_framework import serializers

from apps.board.models import Post, AttachedFile
from apps.manager.constants import *


class AttachedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachedFile
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    attachedfile_set = AttachedFileSerializer(many=True, read_only=True)
    is_permitted_to_read = serializers.SerializerMethodField()
    is_permitted_to_edit = serializers.SerializerMethodField()
    is_permitted_to_delete = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()

    def get_request_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

    def get_is_permitted_to_read(self, obj):
        return obj.is_permitted(self.get_request_user(), PERM_READ)

    def get_is_permitted_to_edit(self, obj):
        return obj.is_permitted(self.get_request_user(), PERM_EDIT)

    def get_is_permitted_to_delete(self, obj):
        return obj.is_permitted(self.get_request_user(), PERM_DELETE)
    
    def get_absolute_url(self, obj):
        return obj.get_absolute_url()

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'content',
            'is_deleted',
            'is_secret',
            'is_permitted_to_read',
            'is_permitted_to_edit',
            'is_permitted_to_delete',
            'absolute_url',
            'board',
            'attachedfile_set'
        )
        depth = 2


class RetrievePostSerializer(serializers.ModelSerializer):
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
