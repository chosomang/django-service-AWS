from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import Metrics


class MetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metrics
        fields = '__all__'
        
        
User = get_user_model()
class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('id', 'password')