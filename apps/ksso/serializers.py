from django.contrib.auth.models import User

from rest_framework import serializers

from apps.ksso.models import PortalInfo


class PortalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortalInfo
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',

            'portal_info',
        )

    portal_info = PortalInfoSerializer()
