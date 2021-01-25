from rest_framework import serializers
from .models import AdminUser, WebsiteInfo, Carousel, Personnel


class AdminUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = AdminUser


class WebsiteInfoSerializer(serializers.Serializer):
    title = serializers.CharField()
    record = serializers.CharField()
    record_switch = serializers.BooleanField()
    maintain = serializers.BooleanField()

    class Meta:
        model = WebsiteInfo


class PersonnelSerializer(serializers.Serializer):
    _id = serializers.IntegerField()
    name = serializers.CharField()
    avatar = serializers.CharField()
    duties = serializers.CharField()

    class Meta:
        model = Personnel


class CarouselSerializer(serializers.Serializer):
    _id = serializers.IntegerField()
    url = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = Carousel