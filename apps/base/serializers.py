from rest_framework import serializers
from apps.base.models import *

class LoginSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','user_type']

class RegisterSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','phone_number','user_type']

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']
