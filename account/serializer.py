from rest_framework import serializers
from .models import AdminUser, WebsiteInfo


class AdminUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = AdminUser


class WebsiteInfoSerializer(serializers.Serializer):
    title = serializers.CharField()
    record = serializers.CharField()
    record_switch = serializers.BooleanField()

    class Meta:
        model = WebsiteInfo
