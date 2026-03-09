from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'is_admin') 
        read_only_fields = ('email',)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:    
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        return value

class ListUserSerializer(serializers.ModelSerializer):
    """Serializer for list User model"""

    class Meta:
        model = User
        fields = ['id','email', 'first_name', 'last_name']

class RetrieveUserSerializer(serializers.ModelSerializer):
    """Serializer for retrieve User model"""

    class Meta:
        model = User
        fields = ['id','email', 'first_name', 'last_name']