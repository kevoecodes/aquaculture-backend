from django.contrib.auth.models import User
from rest_framework import serializers

from aqua.models import UserDevice, Reading


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)


class UserSerializer(serializers.ModelSerializer):

    device_no = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'last_login', 'device_no']

    @staticmethod
    def get_device_no(user):
        user_devices = UserDevice.objects.filter(user=user)
        if len(user_devices) > 0:
            return user_devices[0].device.device_no
        else:
            return None


class ReadingPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reading
        fields = ('ammonia', 'temperature', 'turbidity', 'dissolved_oxygen', 'device')


class ReadingSerializer(serializers.ModelSerializer):
    device_no = serializers.SerializerMethodField()

    class Meta:
        model = Reading
        fields = ('id', 'ammonia', 'created_at', 'temperature', 'turbidity', 'dissolved_oxygen', 'device_no')

    @staticmethod
    def get_device_no(device):
        return device.device.device_no
